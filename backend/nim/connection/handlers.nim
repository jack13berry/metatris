proc serveOptionsConnection(ctx:Ctx, rec:Connection = nil) {.async.} =
  ctx.headers.add("Allow", "OPTIONS, GET, POST, PATCH")


proc serveGetConnection(ctx:Ctx, rec:Connection = nil) {.async.} =
  var rec = if rec == nil: Connection() else: rec
  ctx.body = rec.trmdefault(ctx)
  ctx.contentType = ContentType.html


proc servePostConnection(ctx:Ctx, rec:Connection = nil) {.async.} =
  if ctx.owner == nil:
    ctx.errNoOwner()
    return

  var j :JsonNode
  try:
    j = parseJson(ctx.req.body)
  except JsonParsingError:
    ctx.errBadInput("malformed-json")
    return

  if j.kind != Jarray or j.len != 1:
    ctx.errBadInput("malformed-json")
    return
  
  let recid = ctx.db.insertId(
    sql"""insert into "recs_connection" (owner, grp, "appkey") values (?,?,?)""",
    ctx.owner.id, 0, j[0].getStr
  )

  if not recid > 0:
    ctx.errUndefined("store-failed")
    return
  ctx.body = &"""&{{"result":"ok", "id":"{recid}"}}"""


proc servePatchConnection(ctx:Ctx, rec:Connection = nil) {.async.} =
  if ctx.owner == nil:
    ctx.errNoOwner()
    return

  var j :JsonNode
  try:
    j = parseJson(ctx.req.body)
  except JsonParsingError:
    ctx.errBadInput("malformed-json")
    return

  if j.kind != Jarray:
    ctx.errBadInput("malformed-json")
    return

  var values, assignments :seq[string]

  for ux, upd in j.getElems():
    if upd.kind != Jarray or upd.len < 2 or upd[0].kind != Jint:
      ctx.errBadInput()
      return

    case upd[0].getInt():
    of 0:
      if upd.len == 2: # basic assignment
        assignments.add("appkey = ?")
        values.add(upd[1].getStr())
      
      else:
        ctx.errBadInput()
        return
    
    else:
      ctx.errBadInput()
      return
    
  let updates = assignments.join(", ")
  debugEcho &"UPDATES: `{updates}`"
  let queryOk = ctx.db.tryExec(
    sql("update recs_connection set " & updates), values
  )
  
  if not queryOk:
    ctx.errUndefined("store-failed")
    return
    ctx.body = &"{{\"result\":\"ok\"}}"