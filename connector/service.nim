proc processCommand(cmd:string, client:AsyncSocket) {.async.} =
  var resp :string
  if cmd in cmds:
    resp = await cmds[cmd](client)
    await client.send(resp & "\n")
  else:
    echo &"  unknown command: '{cmd}'"

  # echo &"Comm:\n\tRecv:'{cmd}'\n\tResp:'{resp}'"


proc processClient(client: AsyncSocket) {.async.} =
  while true:
    let line = await client.recvLine()
    if line.len == 0:
      continue

    await processCommand(line, client)


proc serve() {.async.} =
  var server = newAsyncSocket()
  server.setSockOpt(OptReuseAddr, true)
  server.bindAddr(Port(29843), address="127.0.0.1")
  server.listen()

  echo "  server listening"

  while true:
    let client = await server.accept()
    asyncCheck processClient(client)
