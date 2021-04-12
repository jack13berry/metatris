let
  uriApi = "https://metatris.mond.red"
  appId = ".com.metatris.py.1"
  lockey = "oUCUFdhQS14Zm6qAQzRlI7sR96tIQteb" #quickcrypt.generateKey()

  pathConf = normalizedPath( &"{getConfigDir()}/.com.metatris/" )
  sidfilepath = pathFor("sid.cfg")


proc pathFor(flname:string):string =
  return pathConf & os.DirSep & flname
