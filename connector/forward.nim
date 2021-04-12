proc pathFor(flname:string) :string
proc initSession() :Future[string] {.async.}
proc loadSession() :Future[string] {.async.}
proc checkSessionStatus() {.async.}
proc checkSession() {.async.}
proc scheduleSessionStatusCheck() {.async.}
