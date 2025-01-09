rates = input().split(" ")
cases = int(input())
for i in range(cases):
    usage = int(input())
    if (usage > 1000):
        print ("{} {}".format(usage, ((usage-1000)*int(rates[1])+int(rates[0])*1000)))
    else:
        print ("{} {}".format(usage, int(rates[0])*usage))