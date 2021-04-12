proc load(rec:Connection, ctx:Ctx) :bool =
  if rec.version > 0:
    return true

  var row :seq[string] = ctx.db.getRow(
    sql"""select ("owner","grp","appkey") from recs_connection where id=?""",
    rec.id
  )
  if row[0] == "":
    return false

  rec.owner = ctx.loadUser(row[0])
  rec.group = ctx.loadGroup(row[1])
  rec.appkey = row[2]
  return true