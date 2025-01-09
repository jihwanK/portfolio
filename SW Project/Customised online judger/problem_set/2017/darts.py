import math
cases = int(input())
for a in range(cases):
    [w,b,d,s] = map(lambda b : int(b), input().split(" "))
    throwCount = int(input())
    score = 0
    for i in range(throwCount):
        [x,y] = map(lambda b : float(b), input().split(" "))
        r = math.hypot(x,y)
        theta = math.atan2(y,x)
        if (theta < 0):
            theta+=2*math.pi
        throwScore = int(theta/(2*math.pi)*w)+1
        if (r<b):
            score+=50
        elif (r<d):
            score+=throwScore*2
        elif (r<s):
            score+=throwScore
    print(score)