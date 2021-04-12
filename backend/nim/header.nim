func isInvalidUsername(username:string) :bool =
  username == "" or
  username.replace("\"", "").replace("'", "").isEmptyOrWhitespace()


func isInvalidPassword(password:string) :bool =
  password == "" or
  password.replace("\"", "").replace("'", "").isEmptyOrWhitespace()


proc mondHeaderFrom(req :Request) :MondHeader =
  var h = req.headers.getOrDefault("Mond")
  if h == "":
    return nil

  debugEcho &"Found Mond Header: {h}"

  let v = h[1..^1]

  case h[0]:
  of 'c':
    let vals = unpackMondB64(v)
    echo &"Unpacked: <{vals}> {vals.len}"
    if vals.len != 2 or isInvalidUsername(vals[0]) or vals[1] == "":
      return MondHeader(kind:mhKind.malformed)

    return MondHeader(kind:mhKind.credentials, value:v,
      u: vals[0], p: vals[1]
    )
  of 'p':
    return MondHeader(kind:mhKind.appRequest, value:v)
  of 'o':
    return MondHeader(kind:mhKind.ownSession, value:v)
  of 'r':
    return MondHeader(kind:mhKind.rejectSession, value:v)
  of 'd':
    return MondHeader(kind:mhKind.signOut)
  else:
    return MondHeader(kind:mhKind.malformed)


proc handleMondHeader(ctx :Ctx) =
  let mh = mondHeaderFrom(ctx.req)
  if mh == nil:
    return

  ctx.mondHeader = mh

  case mh.kind:
  of mhKind.malformed:
    ctx.errBadInput("malformed-header")

  of mhKind.appRequest:
    ctx.addTempToken(mh.value)
  of mhKind.credentials:
    ctx.checkOwner(mh.u, mh.p)
  of mhKind.signOut:
    ctx.signOut()

  else:
    discard
