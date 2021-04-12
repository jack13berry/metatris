cmds["conf.set"] = proc(client:AsyncSocket) :Future[string] {.async.} =
  let line = await client.recvLine()
  echo &"  saving conf: '{line}'"
  var confreq = await postReq(uriApi & "/conf", line)

  return "ok"
