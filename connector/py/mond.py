import socket, subprocess, time, json

cp = None    # connector process
sock = None  # socket for communication
authdgts = ""
statusLastCheck = 0
lastStatus = 0


def init():
  global sock, cp
  print("  starting mond-connector")
  cp = subprocess.Popen(".\\bin\\metatris-connector.exe")
  sock = socket.create_connection(("127.0.0.1", 29843))

  checkSession()


def quit():
  print("  terminating mond-connector")
  sock.close()
  cp.terminate()
  cp.wait()


def authDigits():
  global authdgts
  if authdgts != "":
    return authdgts

  sock.send("session.digits\n".encode())
  response = sock.recv(4096)
  authdgts = response.decode().strip()
  print ("AUTHDGTS:", authdgts)
  return authdgts


def checkSession():
  sock.send("session.init\n".encode())
  response = sock.recv(4096)
  return response.decode().strip()


def status():
  global lastStatus, statusLastCheck
  now = time.perf_counter()
  if now - 0.6 < statusLastCheck:
    return lastStatus

  sock.send("session.check\n".encode())
  response = sock.recv(4096)
  lastStatus = response.decode().strip()
  statusLastCheck = now

  return lastStatus


def send(kind, msg, expectedSize = 4096):
  sock.send( (kind + "\n" + json.dumps(msg) + "\n").encode() )
  resp = sock.recv(expectedSize).decode().strip()
  return resp
