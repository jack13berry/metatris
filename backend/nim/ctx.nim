proc actionAllowed(ctx:Ctx) :bool =
  true


proc log(ctx:Ctx, msg:string) =
  debugEcho msg


proc errNotFound(ctx:Ctx, err:string = "resource-not-found") {.gcsafe.} =
  ctx.status = Http404
  ctx.contentType = ContentType.json
  ctx.body = &"""{{"err":"{err}"}}"""
  ctx.complete = true


proc errNoOwner(ctx:Ctx, err:string = "login-required") {.gcsafe.} =
  ctx.status = Http401
  ctx.contentType = ContentType.json
  ctx.body = &"""{{"err":"{err}"}}"""
  ctx.complete = true


proc errBadInput(ctx:Ctx, err:string = "malformed-data") {.gcsafe.} =
  ctx.status = Http400
  ctx.contentType = ContentType.json
  ctx.body = &"""{{"err":"{err}"}}"""
  ctx.complete = true


proc errUndefined(ctx:Ctx, err:string = "unexpected-server-failure") {.gcsafe.} =
  ctx.status = Http500
  ctx.contentType = ContentType.json
  ctx.body = &"""{{"err":"{err}"}}"""
  ctx.complete = true


proc addTempToken(ctx:Ctx, appid:string) :string {.discardable,gcsafe.} =
  result = newTempToken()
  echo &"RESULT: '{result}'"
  if not ctx.db.tryExec(
    sql"insert into temptokens (id, session, appid) values (?, ?, ?)",
    result, ctx.sess.id, appid
  ):
    echo &"Could not save temptoken {result}"
    return ""

  ctx.headers.add("Mond", "t" & result)


proc checkOwner(ctx:Ctx, username, password :string) {.gcsafe.} =
  let user = loadUser(ctx, username, password)

  if user == nil:
    ctx.errBadInput("bad-credentials")
    return

  ctx.owner = user
  ctx.sess.owner = user
  storeSessionOwner(ctx, ctx.sess)


proc signOut(ctx:Ctx) {.gcsafe.} =
  discard ctx.db.tryExec(
    sql"update sessions set status=? where id=?",
    int(SessState.signedOut), ctx.sess.id
  )

  ctx.owner = nil
  ctx.sess = newSession(ctx)
  ctx.headers.add("Set-Cookie", ctx.sess.sidCookie(ctx.reqHostName))


proc newCtx(req:Request, db:DbConn) :Ctx =
  let
    ct =
      if req.headers.getOrDefault("Accept").contains("application/json"):
        ContentType.json
      else:
        ContentType.html

    reqHostName =
      if req.headers.hasKey("host"):
        req.headers["host", 0]
      else:
        ""

  var ctx = Ctx(
             db: db,
           logs: newJArray(),
            req: req,
    reqHostName: reqHostName,
        headers: newHttpHeaders([("Content-Type", $ct)]),
         status: Http200,
    contentType: ct
  )

  if reqHostName == "" or not sidCookieDomains.hasKey(reqHostName):
    ctx.errBadInput("Bad Hostname")
    return ctx

  let cstr = req.headers.getOrDefault("Cookie")
  if cstr.len > 0:
    var cs = parseCookies(cstr)
    if cs.hasKey(sidCookieName):
      let sid = cs[sidCookieName]
      if isValidSid(sid):
        ctx.sess = loadSession(ctx, sid)
      else:
        ctx.log(&"Bad SID: '{sid}'")

  if ctx.sess == nil:
    ctx.sess = newSession(ctx)
    ctx.headers.add("Set-Cookie", ctx.sess.sidCookie(ctx.reqHostName))

  elif ctx.sess.owner != nil:
    ctx.owner = ctx.sess.owner

  return ctx
