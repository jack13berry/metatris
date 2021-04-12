type MondReq = ref object
  resp    : AsyncResponse
  sid     : string
  temptkn : string
  body    : string
  errors  : seq[string]


proc makeReq(
    mth:HttpMethod,
    uri:string,
    headers:TableRef[string, string],
    body:string = ""
  ) :Future[MondReq] {.async.} =

  let client = newAsyncHttpClient()
  client.headers = newHttpHeaders()

  if sessionId != "":
    client.headers.add("Cookie", "s=" & sessionId)

  if headers != nil:
    for hname, hval in headers.pairs():
      client.headers.add(hname, hval)

  let response = await client.request(uri, mth)

  let mr = MondReq(resp:response)

  let cookieheader = response.headers.getOrDefault("set-cookie")
  if cookieheader != "":
    let sid = parseCookies(cookieheader).getOrDefault("s")
    mr.sid = sid
  else:
    mr.sid = sessionId

  let hdrTempToken = response.headers.getOrDefault("Mond")
  if hdrTempToken != "":
    mr.temptkn = hdrTempToken[1..^1]
  # echo &"hdrTempToken: '{hdrTempToken}'"

  mr.body = await response.body()

  # echo "mr.body:", mr.body
  return mr


proc postReq(uri:string, body:string, headers:TableRef[string, string] = nil,
  ) :Future[MondReq] {.async.} =

  return await makeReq(HttpPost, uri, headers, body)

proc getReq(uri:string, headers:TableRef[string, string] = nil
  ) :Future[MondReq] {.async.} =

  return await makeReq(HttpGet, uri, headers)
