const
  sidCookieName     = "mettrsd"
  sidCookieLifetime = "31536000"
  sidCookieDomains  = {"metatris.mond.red": true}.toTable

  sidCharset        = {'0'..'9', 'a'..'z', '-'}
  sidLength         = 41
  sidIxDash         = @[15, 21, 27, 33, sidLength-1]

  tempTokLength     = 24
  tempTokIxDash     = @[5, 8, 14, tempTokLength-1]

  randKeyAlphabet   = "0123456789abcdefghijklmnopqrstuvwxyz"
  randKeyAlphSize   = randKeyAlphabet.len
  randTimeDashes    = @[3, 9]

var
  randomizer        = initSystemRandom()


proc randKey(length:int, ixDash:seq[int]) :string =
  var
    ix = 0
    full = int(epochTime() * 1000000)
    sub :int

  result = newString(length)

  for dx in randTimeDashes:
    for x in ix..dx:
      sub = full mod randKeyAlphSize
      result[x] = randKeyAlphabet[sub]
      full = (full - sub) div randKeyAlphSize

    result[dx+1] = '-'
    ix = dx+2

  ix = 10
  for dx in ixDash:
    result[ix] = '-'
    for x in ix+1..dx:
      {.gcsafe.}:
        result[x] = randKeyAlphabet[randomizer.randomInt(0, randKeyAlphSize)]

    ix = dx+1


func isValidSid(sid :string) :bool =
  sid.len == sidLength and allCharsInSet(sid, sidCharset)


proc newSid() :string =
  randKey(sidLength, sidIxDash )


proc newTempToken() :string =
  randKey(tempTokLength, tempTokIxDash)


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


proc storeNewSession(ctx:Ctx, sess:Session) :bool {.discardable.} =
  if sess.owner == nil:
    ctx.db.tryExec(
      sql"insert into sessions (id, owner) values (?, null)",
      sess.id
    )
  else:
    ctx.db.tryExec(
      sql"insert into sessions (id, owner) values (?, ?)",
      sess.id, sess.owner.id
    )

proc storeSessionOwner(ctx:Ctx, sess:Session) :bool {.discardable.} =
  ctx.db.tryExec(
    sql"update sessions set owner=? where id=?",
    sess.owner.id, sess.id
  )


proc newSession(ctx:Ctx, shouldStore:bool=true) :Session =
  let sess = Session(id: newSid())

  if shouldStore:
    storeNewSession(ctx, sess)

  return sess


proc loadSession(ctx:Ctx, sid :string) :Session =
  var row = ctx.db.getRow(
    sql"select status, owner, birth from sessions where id=?", sid
  )

  if row[0] == "":
    echo "Bad Session ID:", sid
    ## **handle bad sid:
    ##    - forged?
    ##    - expired? If so, why not in the database? Do we recycle sids?

    return nil

  let status = SessState(parseInt(row[0]))

  let owner =
    if row[1] == "":
      nil
    else:
      loadUser(ctx, row[1])

  # **refresh session if touch is earlier than <config.N> hours ago
  Session(id: sid, status:status, owner: owner)


proc sessionStatus(ctx:Ctx, sid:string) :SessState =
  var row = ctx.db.getRow( sql"select status from sessions where id=?", sid )
  SessState(parseInt(row[0]))


func sidCookie(sess :Session, dominName: string) :string =
  &"{sidCookieName}={sess.id}; Domain={dominName}; Path=/; " &
      &"Max-Age={sidCookieLifetime}; Secure; SameSite=Lax; HttpOnly"
