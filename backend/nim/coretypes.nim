proc loadTeam(ctx:Ctx, id:string): Team =
  var team = ctx.cachedTeams.getOrDefault(id, nil)
  if team == nil:
    var row = ctx.db.getRow(sql"select name from teams where id=?", id)

    if row[0] == "":
      return nil

    team = Team(id: id, name:row[0])
    ctx.cachedTeams[id] = team

  return team


proc loadUser(ctx:Ctx, id:string) :User =
  var user = ctx.cachedUsers.getOrDefault(id, nil)
  if user == nil:
    var row = ctx.db.getRow(
      sql"select name, team from users where id=?", id
    )

    if row[0] == "":
      return nil

    user = User(id: id, name: row[0], team: loadTeam(ctx, row[1]))
    ctx.cachedUsers[id] = user

  return user


proc loadUser(ctx:Ctx, username, password:string) :User =
  var row = ctx.db.getRow(
    sql"select id, name, team from users where username=? and password=?",
    username, password
  )

  if row[0] == "":
    return nil

  let user = User(id: row[0], name: row[1], team: loadTeam(ctx, row[2]))
  ctx.cachedUsers[row[0]] = user

  return user


proc loadGroup(ctx:Ctx, id:string) :Group =
  var group = ctx.cachedGroups.getOrDefault(id, nil)
  if group == nil:
    var row = ctx.db.getRow(
      sql"select name from groups where id=?", id
    )

    if row[0] == "":
      return nil

    group = Group(id: id, name: row[0])
    ctx.cachedGroups[id] = group

  return group
