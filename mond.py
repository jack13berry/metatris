import socket, subprocess

cp = None    # connector process
sock = None  # socket for communication

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

def checkSession():
  sock.send("session.check\n".encode())
  print("checking session")
  
  response = sock.recv(4096)
  print(f'Received: {response.decode()!r}')


def ready():
  return False