proc loadTeam(ctx:Ctx, id:string): Team =
  var row = ctx.db.getRow(
    sql"select name from teams where id=?",
    id
  )

  if row[0] == "":
    return nil

  return Team(id: id, name:row[0])


proc loadUser(ctx:Ctx, id:string): User =
  var row = ctx.db.getRow(
    sql"select name, team from users where id=?",
    id
  )

  if row[0] == "":
    return nil

  return User(id: id, name:row[0], team:loadTeam(ctx, row[1]))


proc userFromDbRow(ctx:Ctx, row:seq[string]):User =
  User(
    id: row[0],
    name: row[1],
    team: loadTeam(ctx, row[2])
  )
