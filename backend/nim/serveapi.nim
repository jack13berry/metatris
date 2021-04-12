proc serveApiCall(ctx:Ctx, req:Request) {.async.} =
  ctx.contentType = ContentType.json

  let ps = req.url.path.strip(chars={'/'}).split("/")
  case ps[0]:
  of ":a":
    if ctx.owner == nil:
      await serveGetHomepage(ctx)
      ctx.status = Http401
      return

    if ps.len == 3: # /:a/{appId}/{temporary-token}
      let
        appId = ps[1]
        token = ps[2]

      var sessRow = db.getRow(
        sql"select session from temptokens where id=? and appid=?",
        token, appId
      )

      if sessRow[0] == "":
        ctx.status = Http400
        ctx.body = """{"err":"bad-request"}"""
        return

      if ctx.mondHeader == nil:
        discard db.tryExec(
          sql"update sessions set status=?, parent=? where id=?",
          int(SessState.authenticating), ctx.sess.id, sessRow[0]
        )

        var c = Connection()
        c.appkey = digitsFromToken(token)
        await serveGetConnection(ctx, c)
        return

      elif ctx.mondHeader.kind == mhKind.ownSession:
        discard ctx.db.tryExec(
          sql"update sessions set status=?, owner=? where id=? and parent=?",
          int(SessState.owned),
          ctx.owner.id,
          sessRow[0], ctx.sess.id
        )
        ctx.body = """{"result":"ok"}"""
        return

      elif ctx.mondHeader.kind == mhKind.rejectSession:
        discard ctx.db.tryExec(
          sql"update sessions set status=?, owner=? where id=? and parent=?",
          int(SessState.rejected),
          1, # ctx.owner.id,
          sessRow[0], ctx.sess.id
        )
        ctx.body = """{"result":"ok"}"""
        return

  of ":s":
    case ctx.sess.status:
    of SessState.owned:
      ctx.body = """{"result":"ok"}"""
    of SessState.rejected:
      ctx.body = """{"result":"rejected"}"""
    else:
      var
        callx  = 0
        status = SessState.authenticating

      while callx<100 and status == SessState.authenticating:
        callx += 1
        await sleepAsync(200)
        status = sessionStatus(ctx, ctx.sess.id)

      ctx.body = "{\"result\":\"" & (
        case status:
        of SessState.owned: "ok"
        of SessState.rejected: "rejected"
        else: "waiting"
      ) & "\"}"

  of ":schck":
    if ctx.sess.status == SessState.owned:
      ctx.body = """{"result":"ok"}"""
    else:
      ctx.status = Http401
      ctx.body = """{"result":"unauthorized"}"""
  
  of ":gameplay":
    # ctx.body = &"serving `{$ctx.req.reqMethod} - Gameplay`\n\n```\n{ctx.req.body}\n```\n"
    let id = if ps.len > 1: ps[1] else: ""
    case req.reqMethod:
    of HttpGet:
      if id == "":
        await serveGetGameplayList(ctx)
      else:
        await serveGetGameplay(ctx, id)
    of HttpPatch:
      await servePatchGameplay(ctx, id)
    of HttpPost:
      await servePostGameplay(ctx)
    of HttpOptions:
      await serveOptionsGameplay(ctx, id)
    else:
      ctx.status = Http405
  
  else:
    ctx.status = Http400
