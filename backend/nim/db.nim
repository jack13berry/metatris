
var db {.threadVar.} :DbConn

proc connectToDb() :bool =
  var
    host = getEnv("DBHOST")
    port = getEnv("DBPORT", "5433")
    user = getEnv("DBUSER", "metatris")
    pass = getEnv("DBPASS", "pass-metatris-pass")
    dbnm = getEnv("DB", "metatris")
    tout = getEnv("DBCONNTIMEOUT", "2")
    rtry = parseInt( getEnv("DBMAXRETRY", "10") )

  var retries = 0
  while db == nil:
    try:
      echo &"Will connect to DB at '{host}' on port '{port}' as '{user}'"
      db = open("","","",
        &"host={host} port={port} dbname={dbnm} user={user} password={pass}" &
        &" connect_timeout={tout}"
      )

    except:
      echo "Cannot connect to database:", getCurrentExceptionMsg()
      echo "Will try again..."
      sleep(2400)

      retries += 1
      if retries == rtry:
        return false

  return true
