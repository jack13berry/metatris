var
  sessionAuthorized  :bool = false
  sessionRejected    :bool = false
  sessionTempToken   :string
  sessionTempDigits  :string


cmds["session.init"] = proc(client:AsyncSocket) :Future[string] {.async.} =
  if fileExists(sidfilepath):
    echo &"session found {sidfilepath}"
    return await loadSession()
  else:
    echo &"session not found"
    return await initSession()

  return "no-session"


cmds["session.check"] = proc(client:AsyncSocket) :Future[string] {.async.} =
  if sessionAuthorized:
    return "authorized"
  if sessionRejected:
    return "rejected"

  return "waiting"


cmds["session.digits"] = proc(client:AsyncSocket) :Future[string] {.async.} =
  if sessionAuthorized or sessionRejected:
    return ""

  return sessionTempDigits


func digitsFromToken(token :string) :string =
  var
    s = ""
    i = 0
    p = char(0)

  while s.len < 6:
    i += 2
    if i >= token.len:
      i = 1

    if token[i] != p:
      p = token[i]
      s &= $( p.ord() mod 10 )

  return s


proc initSession() :Future[string] {.async.} =
  var headers = newTable[string, string]()
  headers["Mond"] = &"p{appId}"

  var mr = waitFor getReq(uriApi & "/", headers)

  while mr == nil or mr.temptkn == "":
    sleep(1)
    mr = waitFor getReq(uriApi & "/", headers)

  sessionTempToken = mr.temptkn
  sessionTempDigits = digitsFromToken(mr.temptkn)
  echo &"SESSIONDIGITS: '{sessionTempDigits}'"

  openInDefaultApp(&"{uriApi}/:a/{appId}/{mr.temptkn}")

  var sidfile = open(sidfilepath, fmWrite)
  sidfile.write(mr.sid.encrypt(lockey))
  sidfile.close()

  sessionId = mr.sid
  asyncCheck checkSessionStatus()

  return "started"


proc loadSession() :Future[string] {.async.} =
  var sidfile = open(sidfilepath, fmRead)
  let sid = sidfile.readAll().decrypt(lockey)
  sidfile.close()

  asyncCheck checkSession()

  sessionId = sid

  return "started"


proc checkSession() {.async.} =
  sessionAuthorized = true
  #** check if session is still valid


proc scheduleSessionStatusCheck() {.async.} =
  await sleepAsync(9_500)
  if not sessionAuthorized and not sessionRejected:
    asyncCheck checkSessionStatus()


var srx = 0

proc checkSessionStatus() {.async.} =
  asyncCheck scheduleSessionStatusCheck()

  srx += 1
  echo &"sending request: {$srx}"

  let sr = await getReq(uriApi & "/:s")
  if sr == nil:
    echo "server down, will wait..."
    return

  echo &"got response[{$srx}]: '{sr.body}'"

  case sr.body:
  of """{"result":"ok"}""":
    sessionAuthorized = true
  of """{"result":"rejected"}""":
    sessionRejected = true
  else:
    echo "waiting for user approval..."
