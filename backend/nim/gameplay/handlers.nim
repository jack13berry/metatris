proc serveOptionsGameplay(ctx:Ctx, id:string) {.async.} =
  ctx.headers.add("Allow", "OPTIONS, GET, POST, PATCH")


proc serveGetGameplay(ctx:Ctx, id:string) {.async.} =
  var rec = Gameplay(id:id)
  if not rec.load(ctx):
    ctx.errNotFound()
    return
  ctx.body = rec.trmdefault(ctx)
  ctx.contentType = ContentType.html


proc serveGetGameplayList(ctx:Ctx) {.async.} =
  if ctx.owner == nil:
    ctx.errNoOwner()
    return

  var rows:seq[seq[string]]
  
  for row in ctx.db.fastRows(
    sql"""select owner, grp, "config" from recs_gameplay 
        order by birth desc""",
  ):
    rows.add(row)
  ctx.contentType = ContentType.json
  ctx.body = $(%*(rows))


proc servePostGameplay(ctx:Ctx) {.async.} =
  if ctx.owner == nil:
    ctx.errNoOwner()
    return

  var j :JsonNode
  try:
    j = parseJson(ctx.req.body)
  except JsonParsingError:
    ctx.errBadInput("malformed-json")
    return

  if j.kind != Jarray or j.len != 2:
    ctx.errBadInput("malformed-json")
    return
  
  let recid = ctx.db.insertId(
    sql"""insert into "recs_gameplay" (owner, grp, "config", "timeline") values (?,?,?,?)""",
    ctx.owner.id, 0, $(j[0]), toSqlList(j[1])
  )

  if not recid > 0:
    ctx.errUndefined("store-failed")
    return
  ctx.body = &"""&{{"result":"ok", "id":"{recid}"}}"""


proc servePatchGameplay(ctx:Ctx, id:string) {.async.} =
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
        assignments.add("config = ?")
        values.add($(upd[1]))
      
      else:
        ctx.errBadInput()
        return
    
    of 1:
      if upd.len == 2: # basic assignment
        assignments.add("timeline = ?")
        values.add(toSqlList(upd[1]))
      
      elif upd[1].kind != Jint:
        ctx.errBadInput()
        return

      let opcode = upd[1].getInt()
      if opcode > 7 or opcode < 3:
        ctx.errBadInput()
        return

      case opcode:
      of 6:
        if upd.len != 5 or upd[2].kind != Jint or upd[3].kind != Jint or upd[4].kind != Jarray:
          ctx.errBadInput()
          return

        let
          ixLeft = upd[2].getInt()
          ixRght = upd[3].getInt()

        assignments.add(&"timeline[{ixLeft}:{ixRght}] = ?")
        values.add(toSqlList(upd[4]))

    
      else:
        ctx.errBadInput()
        return
    
    else:
      ctx.errBadInput()
      return
    
  let updates = assignments.join(", ")
  debugEcho &"UPDATES: `{updates}`"
  let queryOk = ctx.db.tryExec(
    sql("update recs_gameplay set " & updates), values
  )
  
  if not queryOk:
    ctx.errUndefined("store-failed")
    return
    ctx.body = &"{{\"result\":\"ok\"}}"