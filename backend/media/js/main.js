var MH, MFFN, MGFN, m
MH = {}
MXFN = {}
MFFN = {}
MGFN = {}
m = {
  rid:0
}
function cix(n) {
  var x, p=n.parentNode, l=p.childElementCount
  for (x=0;x<l;x++) { if (n == p.children[x]) return x; }
  return -1
}
function eh(n,q,e,h) {
  var ex, es = n.querySelectorAll(q)
  for (ex=0;ex<es.length;ex++) {
    es[ex].addEventListener(e,h)
  }
}
function lm(e) {
  var u = this.getAttribute("href")
  e.preventDefault()
  e.stopImmediatePropagation()
  this.blur()
  return false
}
function handled (evt) {
  evt.stopPropagation()
  evt.stopImmediatePropagation()
  evt.preventDefault()
  return false
}

m.partition = function(str) { // sep, ...
  var parts = str.split(arguments[1])
  for (px=0;px<parts.length;px++) {
    parts[px] = parts[px].trim()
  }

  if (arguments.length == 2) {
    return parts
  }
  var px, ax, args
  for (px=0;px<parts.length;px++) {
    args = [parts[px]]
    for (ax=2;ax<arguments.length;ax++) args.push(arguments[ax]);
    parts[px] = m.partition.apply(null, args)
  }
  return parts
}

m.copy = function(str) {
  var i = document.createElement('textarea')
  i.setAttribute('type', 'text')
  i.innerText = str
  i.style.position = 'absolute'
  i.style.left = '-1px'
  i.style.width = '1px'
  i.style.height = '1px'
  document.body.appendChild(i)
  i.select()
  document.execCommand("copy")
  document.body.removeChild(i)
}
;(function() {

  function req(uri, method, body, contentType, headers, cbok, cberr) {
    var xhr, r

    xhr = new XMLHttpRequest()
    xhr.open(method, uri)
    r = { xhr:xhr, cbok:cbok, cberr:cberr }

    if (contentType !== "") {
      xhr.setRequestHeader('Content-Type', contentType)
    }

    var hx, h
    for (hx=0; hx<headers.length; hx++) {
      h = headers[hx]
      xhr.setRequestHeader(h[0], h[1])
    }

    xhr.onreadystatechange = function () {
      if (xhr.readyState !== XMLHttpRequest.DONE) {
        return
      }
      var s = xhr.status
      if (s === 0 || (s >= 200 && s < 400)) {
        var rawResponse = xhr.responseText
        var response
        if (rawResponse === "") {
          response = ""
        } else {
          try {
            response = JSON.parse(rawResponse)
          } catch {
            response = "err" // m.Error("malformed-response")
          }
        }
        r.cbok.call(xhr, response)
      } else {
        r.status = s
        r.cberr.call(xhr, s)
      }
    }
    if (body) {
      xhr.send(body)
    } else {
      xhr.send()
    }
    return r
  }

  m.req = function(uri, prms) {
    function hok() {
      console.log("m.req[Ok]:", uri, this.status, this.responseText)
    }
    function herr() {
      console.log("m.req[Err]:", uri, this.status, this.responseText)
    }
    if (!prms) {
      return req(uri, 'GET', '', '', [], hok, herr)
    }
    if (typeof prms === "function") {
      return req(uri, 'GET', '', '', [], prms, herr)
    }

    return req(uri,
      (prms.method || 'get').toUpperCase(),
      (prms.body || ''),
      (prms.contentType || ''),
      (prms.headers || []),
      (prms.ok || hok),
      (prms.err || herr),
    )
  }

  m.reqOld = function(uri, method, body, contentType, headers, cbok, cberr) {
    function hok() {
      console.log("m.req[Ok]:", uri, this.status, this.responseText)
    }
    function herr() {
      console.log("m.req[Err]:", uri, this.status, this.responseText)
    }
    function rmUndefined(a) { return !!a }

    if (arguments.length === 1) { return req(uri, "GET", "", "", [], hok, herr) }
    else if (arguments.length === 7) {
      return req(uri, method.toUpperCase(), body, contentType, headers,
        cbok, cberr)
    }

    // 2 < arguments < 7:
    var args = [method, body, contentType, headers, cbok].filter(rmUndefined)
    var ax = 0
    if (typeof args[0] === "string") {
      method = method.toUpperCase()
      if (typeof args[1] === "string") {
        if (typeof args[2] === "string") {
          ax+=3
        }
        else {
          ax+=2
          contentType = "application/json"
        }
      } else {
        ax++
        body = ""
        contentType = "application/json"
      }
    } else {
      method = "GET"
    }

    if (args[ax] instanceof Array) {
      headers = args[ax]
      ax++
    } else {
      headers = []
    }

    if (ax < args.length - 1) {
      cbok = args[ax]
      cberr = args[ax+1]
    } else {
      cberr = herr
      if (ax < args.length) {
        cbok = args[ax]
      } else {
        cbok = hok
      }
    }

    // console.log("REQ:", uri, method, body, contentType, headers, cbok, cberr)
    return req(uri, method, body, contentType, headers, cbok, cberr)

  }

})();
;(function(){

function parseMex(mex) {
  var mx, mexs, result
  result = []
  mexs = mex.split(" ")
  for (mx=0; mx<mexs.length; mx++) {
    result.push( mexs[mx].split(";") )
  }
  return result
}

function fillContent(d, val, hier) {
  var formattingFn = MFFN[d.getAttribute('mffn')]
  if (formattingFn) {
    val = formattingFn(val, hier)
  }

  if (val instanceof Array) {
    var parent = d
    d = parent.firstElementChild

    var emptyListTemplate = d.nextElementSibling
    if (emptyListTemplate) {
      parent.removeChild(emptyListTemplate)
    } else {
      emptyListTemplate = document.createElement("div")
    }
    if (val.length === 0) {
      while (d) {
        parent.removeChild(d)
        d = parent.firstElementChild
      }
      parent.appendChild(emptyListTemplate)
      m.pmhs(emptyListTemplate)
      return
    }

    var groupingFn, groupTemplate, groupNode
    groupTemplate = d.nextElementSibling
    if (groupTemplate) {
      parent.removeChild(groupTemplate)
      groupingFn = MGFN[groupTemplate.getAttribute("mgfn")]
    }

    parent.removeChild(d)

    var item, ix, prevItem, nextItem, itemNode
    for (ix=0; ix<val.length; ix++) {
      item = val[ix]
      if (groupingFn) {
        prevItem = val[ix-1] || null
        nextItem = val[ix+1] || null

        groupNode = groupingFn(
          groupTemplate, item, ix, prevItem, nextItem, hier)

        if (groupNode) {
          parent.appendChild(groupNode)
          m.pmhs(groupNode)
        }
      }

      itemNode = m.fillTemplate(d, item, hier)
      processElm(itemNode, item, hier)
      parent.appendChild( itemNode )
      m.pmhs(itemNode)
    }
  }
  else if (typeof val === 'object') {
    m.fillTemplate(d, val, hier, true)
  } else {
    d.innerHTML = val
    m.pmhs(d, false)
  }
}

function processMex(m, d, obj, hier) {
  var val

  if (m[0][0] === ".") {
    val = MXFN[m[0].substr(1)](obj, hier, d)
  } else {
    val = obj[m[0]]
  }

  if (m.length === 1) {
    fillContent(d, val, hier.concat([obj]))
  } else if (m.length === 2) {
    if (m[1] === '.') {
      if (val !== '') {
        d.classList.add(val)
      }
    }
    else if (m[1] !== '@') {
      d.setAttribute( m[1], val )
    }
  }
}

function processElm(elm, obj, hier) {
  var mexstr, mexs
  mexstr = elm.getAttribute('mex')
  if (!mexstr) { return }
  mexs = parseMex( mexstr )
  for (mx=0; mx<mexs.length; mx++) {
    processMex(mexs[mx], elm, obj, hier)
  }
}

function dynElmsOf(parent) {
  var dx, dynelms, d, p, matched, isRoot
  dynelms = parent.querySelectorAll('[mex]')
  matched = []

  for (dx=0; dx<dynelms.length; dx++) {
    d = dynelms[dx]
    p = d.parentElement
    isRoot = true
    while (p !== parent) {
      if (p.getAttribute('mex')) {
        isRoot = false
        break
      }
      p = p.parentElement
    }
    if (isRoot) {
      matched.push(dx)
    }
  }

  for (dx=0;dx<matched.length;dx++) {
    matched[dx] = dynelms[matched[dx]]
  }

  return matched
}

m.fillTemplate = function(template, obj, hier, dontClone) {
  var dx, d, elm, dynelms, mx, mexs

  if (dontClone) {
    elm = template
  } else {
    elm = template.cloneNode(true)
    if (template.parentElement) {
      template.parentElement.removeChild(template)
    }
  }
  elm.mobj = obj
  dynelms = dynElmsOf(elm)
  // console.log("DynElms:")
  // console.log(dynelms)

  for (dx=0; dx<dynelms.length; dx++) {

    d = dynelms[dx]
    // if (d.mUsed) { continue }
    processElm(d, obj, hier)
    // mexs = parseMex( d.getAttribute('mex') )
    // for (mx=0; mx<mexs.length; mx++) {
    //   processMex(mexs[mx], d, obj, hier)
    // }

    // d.mUsed = true

  }

  return elm
}

})();
;(function() {

m.login = function(username, password) {

  function cbok() {
    window.location.reload()
  }
  function cberr() {
    console.log("ERR:", arguments)
  }

  var u, p, mh
  u = btoa(username)
  p = btoa(password)
  mh = 'c'+u.length + '-' + p.length + '/'+u+p
  m.req('', 'get', [['Mond', mh]], cbok, cberr)
}

m.logout = function() {
  function cbok() {
    window.location.reload()
  }
  function cberr() {
    console.log("ERR:", arguments)
  }

  m.req('', 'get', [['Mond', 'd-']], cbok, cberr)
}

function pmhs(elm) {
  var defs, dx, d
  defs = m.partition(elm.getAttribute("mh"), ";", ":")
  for (dx=0; dx<defs.length; dx++) {
    d = defs[dx]
    if (d.length === 2) {
      elm.addEventListener(d[0], MH[d[1]])
    } else {
      elm.addEventListener("click", MH[d[0]])
    }
  }
}

m.pmhs = function(root, includeRoot){
  var ex, elms
  if (includeRoot !== false && root.getAttribute('mh')) { pmhs(root) }
  elms = root.querySelectorAll("[mh]")
  for (ex=0; ex<elms.length; ex++) { pmhs(elms[ex]) }
}

})();


// Functions for doc[default]:
function postAppAuth (decision) {
var code = [
  "<p>Game login accepted. Enjoy playing!</p>",
  "<p>Game login rejected. If this was by accident, please restart the game to retry.</p></p>",
]
return function() { // 0:approved, 1:rejected
  document.querySelector("body>main").innerHTML = '<div class="infobox">'+
    code[decision] + '</div>'
  setTimeout(function(){window.location="/"}, 5000)
}
}
MH["login"] = function (evt) {
m.login(
  this.querySelector("input[autocomplete='username']").value,
  this.querySelector("input[autocomplete='current-password']").value
)
return handled(evt)
}
MH["logout"] = function (evt) {
m.logout()
return handled(evt)
}
MH["approve-app-login"] = function (evt) {

var tkn = window.location.pathname.split("/").pop()
m.req(location.pathname, { 
  headers: [["Mond", "o"+tkn]], 
  ok: postAppAuth(0)
})
return handled(evt)
}
MH["reject-app-login"] = function (evt) {
function inform() { document.querySelector("body>main").innerHTML="REJECTED" }
var tkn = window.location.pathname.split("/").pop()
m.req(location.pathname, {
  headers: [["Mond", "r"+tkn]], 
  ok: postAppAuth(1)
})
return handled(evt)
}
MH["download"] = function (evt) {
download('https://memberfiles.metatris.com/installer/'+
  this.getAttribute('mh-download'))
return handled(evt)
}

// End of Functions for doc[default].

addEventListener("DOMContentLoaded",function(){
  var f = document.querySelector('[m="fol"]')
  if (f) { f.focus() }
  m.pmhs(document, false)
  if (MH.init && MH.init.call) { MH.init() }
})
