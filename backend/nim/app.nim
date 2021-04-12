# Mond App: Metatris Metatris Backend [metatris.backend]

import
  # strmisc, osproc, streams,
  strutils, strformat, strtabs, os, json, base64, tables,
  json, times, httpcore, cookies, asynchttpserver, asyncdispatch,
  db_postgres, pkg/random

from posix import onSignal, SIGINT, SIGTERM

let
  envIsProd :bool = getEnv("ENV") == "PROD"

include ./types

proc errNotFound(ctx:Ctx, err:string = "resource-not-found") {.gcsafe.}
proc errNoOwner(ctx:Ctx, err:string = "login-required") {.gcsafe.}
proc errBadInput(ctx:Ctx, err:string = "malformed-data") {.gcsafe.}
proc errUndefined(ctx:Ctx, err:string = "unexpected-server-failure") {.gcsafe.}

proc addTempToken(ctx:Ctx, appid:string) :string {.discardable,gcsafe.}
proc signOut(ctx:Ctx) {.gcsafe.}
proc checkOwner(ctx:Ctx, username, password :string) {.gcsafe.}

include ./util
include ./header
include ./db
include ./coretypes
include ./auth
include ./session

include ./homepage/trims
include ./homepage/handlers
include ./downloadpage/trims
include ./downloadpage/handlers
include ./teampage/trims
include ./teampage/handlers
include ./connection/trims
include ./connection/handlers
include ./gameplay/rw
include ./gameplay/trims
include ./gameplay/handlers

include ./ctx
include ./serveapi
include ./service