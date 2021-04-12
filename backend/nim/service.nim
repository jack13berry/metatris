let
  cnfHttpHost = getEnv("HTTPHOST", "0.0.0.0")
  cnfHttpPort = parseInt( getEnv("HTTPPORT", "8080") )


proc handle(req: Request) {.async, gcsafe.}


# main:
var server :AsyncHttpServer

onSignal(SIGINT, SIGTERM):
  echo "metatris.backend received signal. Shutting down..."
  if db != nil:
    db.close()
  if server != nil:
    server.close()

  quit(0)


if not connectToDb():
  echo "Cannot start without connection to DB. Will quit"
  quit(1)

echo "DB connection established. metatris.backend" &
  &" listens on {cnfHttpHost}:{$cnfHttpPort}..."

server = newAsyncHttpServer()

waitFor server.serve(Port(cnfHttpPort), handle, address=cnfHttpHost)
# main.


proc serveWebCall(ctx:Ctx, req:Request) {.async.} =
  ctx.contentType = ContentType.json

  var uriRow = db.getRow(
    sql"select kind, id, doc from uris where path=?",
    req.url.path[1..^1]
  )

  if uriRow[0] == "":
    ctx.status = Http404
    ctx.body = &"Not Found: `{req.url.path}`"
    return

  let
    recType = RtKind(parseInt(uriRow[0]))
    recId = uriRow[1]
    # recDoc = parseInt(uriRow[2])
  
  case recType:
  of rtkGameplay:
    if req.reqMethod == HttpGet:
      await serveGetGameplay(ctx, recId)
    elif req.reqMethod == HttpOptions:
      await serveOptionsGameplay(ctx, recId)
  else:
    await req.respond(Http400, "Bad Request", ctx.headers)
    return


proc handle(req:Request) {.async, gcsafe.} =

  var ctx = newCtx(req, db)

  echo &"Serving {req.reqMethod} {ctx.reqHostName}{req.url.path}"

  if ctx.sess != nil and ctx.sess.owner != nil:
    echo &"sess owner: {ctx.sess.owner.name} - {ctx.sess.id}"
  if ctx.complete:
    await req.respond(ctx.status, ctx.body, ctx.headers)
    return

  handleMondHeader(ctx)

  if ctx.complete:
    await req.respond(ctx.status, ctx.body, ctx.headers)
    return

  case req.url.path:
  of "/":
    if req.reqMethod == HttpGet:
      await serveGetHomePage(ctx)
    elif req.reqMethod == HttpOptions:
      await serveOptionsHomePage(ctx)
  of "/download":
    if req.reqMethod == HttpGet:
      await serveGetDownloadPage(ctx)
    elif req.reqMethod == HttpOptions:
      await serveOptionsDownloadPage(ctx)
  of "/the-team":
    if req.reqMethod == HttpGet:
      await serveGetTeamPage(ctx)
    elif req.reqMethod == HttpOptions:
      await serveOptionsTeamPage(ctx)


    await req.respond(Http200, ctx.body, ctx.headers)
    return

  else:
    if req.url.path.startsWith("/:"):
      await serveApiCall(ctx, req)
    else:
      await serveWebCall(ctx, req)

  ctx.headers.add("Content-Type", $(ctx.contentType))
  await req.respond(ctx.status, ctx.body, ctx.headers)
