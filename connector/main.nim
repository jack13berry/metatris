import strformat, tables, os, strtabs, cookies,
  asyncnet, asyncdispatch, httpclient,
  quickcrypt, os_files/file_info

var
  sessionId:string
  cmds = initTable[string, proc(client:AsyncSocket):Future[string] {.async.}]()

include ./forward
include ./base

if not dirExists(pathConf):
  createDir(pathConf)

include ./req
include ./cmd/session
include ./cmd/conf
include ./service

asyncCheck serve()
runForever()
