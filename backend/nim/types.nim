type
  Error = string

  ContentType {.pure.} = enum
    json = "application/json"
    html = "text/html"
    text = "text/plain"
    csv  = "text/csv"
    zip  = "application/zip"

  Team = ref object
    id     :string
    name   :string

  User = ref object
    id     :string
    name   :string
    team   :Team

  Group = ref object
    id     :string
    name   :string

  SessState {.pure.} = enum
    anon           = 0
    owned          = 1
    authenticating = 2
    rejected       = 3
    signedOut      = 4

  Session = ref object
    id     :string
    status :SessState
    owner  :User
    


  mhKind {.pure.} = enum
    malformed     = 0
    credentials   = 1
    appRequest    = 2
    ownSession    = 3
    rejectSession = 4
    signOut       = 5

  MondHeader = ref object
    value :string

    case kind :mhKind
    of mhKind.malformed:
      errorInfo :string
    of mhKind.credentials:
      u: string
      p: string
    of mhKind.appRequest:
      discard
    of mhKind.ownSession:
      discard
    of mhKind.rejectSession:
      discard
    of mhKind.signOut:
      discard


  Ctx = ref object
    db           :DbConn
    logs         :JsonNode

    req          :Request
    reqHostName  :string
    prms         :string

    docTrim      :int

    sess         :Session
    owner        :User

    cachedUsers  :Table[string,User]
    cachedTeams  :Table[string,Team]
    cachedGroups :Table[string,Group]

    complete     :bool
    mondHeader   :MondHeader
    headers      :HttpHeaders
    status       :HttpCode
    contentType  :ContentType

    body         :string

  RtKind = enum
    rtkUndefined
    rtkHomePage
    rtkDownloadPage
    rtkTeamPage
    rtkConnection
    rtkGameplay

  HomePage = ref object 
    id      :string
    version :int
    owner   :User
    group   :Group
    title :string # Title

  DownloadPage = ref object 
    id      :string
    version :int
    owner   :User
    group   :Group
    title :string # Title

  TeamPage = ref object 
    id      :string
    version :int
    owner   :User
    group   :Group
    title :string # Title

  Connection = ref object 
    id      :string
    version :int
    owner   :User
    group   :Group
    appkey :string # AppKey

  Gameplay = ref object 
    id      :string
    version :int
    owner   :User
    group   :Group
    config :string # GameConfig
    timeline :seq[string] # Timeline
