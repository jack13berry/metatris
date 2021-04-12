func unpackMondB64(pack:string) :seq[string] =
  let
    lr      = pack.split('/', 1)
    marks   = lr[0]
    elems   = lr[1]
    lengths = marks.split('-')

  var
    lst = newSeqOfCap[string](lengths.len)
    ix = 0

  for lns in lengths:
    let ln = parseInt(lns)
    lst.add( elems[ix..ix+ln-1].decode() )
    ix = ix+ln

  return lst


proc fromSqlListItem[T](str: string) :T =
  if T is JsonNode:
    return parseJson(str)
  elif T is string:
    return str


proc toSqlList(lst :JsonNode) :string =
  var elms: seq[string]
  for n in lst.getElems():
    elms.add( escape($n) )

  result = "{" & elms.join(",") & "}"
