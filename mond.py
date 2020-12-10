import socket, subprocess, time

cp = None    # connector process
sock = None  # socket for communication
authdgts = ""

def init():
  global sock, cp
  print("starting mond-connector")
  cp = subprocess.Popen(".\\bin\\metatris-connector.exe")
  sock = socket.create_connection(("127.0.0.1", 29843))

  checkSession()


def quit():
  print("Terminating mond-connector")
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


statusLastCheck = 0
lastStatus = 0

def status():
  sock.send("session.check\n".encode())
  response = sock.recv(4096)
  return response.decode().strip()
