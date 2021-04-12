import time, mond

t1 = time.perf_counter()

print("0. Initializing", t1)

mond.init()

t2 = time.perf_counter()
print("1. Opening session %0.4f" % (t2 - t1))
t1 = t2

for i in range(1,10):
  s = mond.status()

  if s == "waiting":
    print ("  status:", s)
    print ("  digits:", mond.authDigits())
  else:
    print ( "  authorized")
    break

  time.sleep(1)

t2 = time.perf_counter()
print("2. Sending a message %0.4f" % (t2 - t1))
t1 = t2

resp = mond.send("conf.set", {
  "a":3,
  "x":"foobar"
})

print("  resp: ```%s```" % resp)

t2 = time.perf_counter()
print("X. Closing %0.4f" % (t2 - t1))
mond.quit()
