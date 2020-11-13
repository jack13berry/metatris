

# Timing of the original NES NTSC. Frame rate: 60.0988fps

# levels            00  01  02  03  04  05  06  07 08 09 10
# frames per drop   48  43  38  33  28  23  18  13  8  6  5
# levels            11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29
# frames per drop   5  5  4  4  4  3  3  3  2  2  2  2  2  2  2  2  2  2  1

class TimingSetup():
  pass

NesNtsc = TimingSetup()
NesNtsc.dasWaitTime = 0.2662282774
NesNtsc.dasRepeatTime = 0.09983560404

NesNtsc.levels = [
  0.79868483230,  # Lvl:00    F:48
  0.71548849560,  # Lvl:01    F:43
  0.63229215890,  # Lvl:02    F:38
  0.54909582220,  # Lvl:03    F:33
  0.46589948550,  # Lvl:04    F:28
  0.38270314880,  # Lvl:05    F:23
  0.29950681210,  # Lvl:06    F:18
  0.21631047540,  # Lvl:07    F:13
  0.13311413870,  # Lvl:08    F: 8
  0.09983560404,  # Lvl:09    F: 6
  0.08319633670,  # Lvl:10    F: 5
  0.08319633670,  # Lvl:11    F: 5
  0.08319633670,  # Lvl:12    F: 5
  0.06655706936,  # Lvl:13    F: 4
  0.06655706936,  # Lvl:14    F: 4
  0.06655706936,  # Lvl:15    F: 4
  0.04991780202,  # Lvl:16    F: 3
  0.04991780202,  # Lvl:17    F: 3
  0.04991780202,  # Lvl:18    F: 3
  0.03327853468,  # Lvl:19    F: 2
  0.03327853468,  # Lvl:20    F: 2
  0.03327853468,  # Lvl:21    F: 2
  0.03327853468,  # Lvl:22    F: 2
  0.03327853468,  # Lvl:23    F: 2
  0.03327853468,  # Lvl:24    F: 2
  0.03327853468,  # Lvl:25    F: 2
  0.03327853468,  # Lvl:26    F: 2
  0.03327853468,  # Lvl:27    F: 2
  0.03327853468,  # Lvl:28    F: 2
  0.01663926734   # Lvl:29    F: 1
]


NesPal = TimingSetup()
NesPal.dasWaitTime = 0.2399664047
NesPal.dasRepeatTime = 0.07998880157

NesPal.levels = [
  0.71989921410,  # Lvl:00    F:36
  0.63991041250,  # Lvl:01    F:32
  0.57991881140,  # Lvl:02    F:29
  0.49993000980,  # Lvl:03    F:25
  0.43993840860,  # Lvl:04    F:22
  0.35994960710,  # Lvl:05    F:18
  0.29995800590,  # Lvl:06    F:15
  0.21996920430,  # Lvl:07    F:11
  0.13998040270,  # Lvl:08    F: 7
  0.09998600196,  # Lvl:09    F: 5
  0.07998880157,  # Lvl:10    F: 4
  0.07998880157,  # Lvl:11    F: 4
  0.07998880157,  # Lvl:12    F: 4
  0.05999160118,  # Lvl:13    F: 3
  0.05999160118,  # Lvl:14    F: 3
  0.05999160118,  # Lvl:15    F: 3
  0.03999440078,  # Lvl:16    F: 2
  0.03999440078,  # Lvl:17    F: 2
  0.03999440078,  # Lvl:18    F: 2
  0.01999720039,  # Lvl:19    F: 1
  0.01999720039,  # Lvl:20    F: 1
  0.01999720039,  # Lvl:21    F: 1
  0.01999720039,  # Lvl:22    F: 1
  0.01999720039,  # Lvl:23    F: 1
  0.01999720039,  # Lvl:24    F: 1
  0.01999720039,  # Lvl:25    F: 1
  0.01999720039,  # Lvl:26    F: 1
  0.01999720039,  # Lvl:27    F: 1
  0.01999720039,  # Lvl:28    F: 1
  0.01999720039   # Lvl:29    F: 1
]