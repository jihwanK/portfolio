modes = ["AIR","SEA","RAIL","TRUCK"]
cases = int(input())
for a in range(cases):
    c = int(input())
    adjList =list(map(lambda x : {}, range(4*c+2)))
    cityMap={}
    for b in range (c):
        cityLine = input().split(" ")
        cityMap[cityLine[0]]=b
        for i in range(4):
            for j in range(4):
                adjList[i*c+b][j*c+b] = int(cityLine[1])
    e = int(input())
    for b in range(e):
        edgeLine = input().split(" ")
        mode = modes.index(edgeLine[2])
        adjList[mode*c+cityMap[edgeLine[0]]][mode*c+cityMap[edgeLine[1]]]=adjList[mode*c+cityMap[edgeLine[1]]][mode*c+cityMap[edgeLine[0]]]=int(edgeLine[3])
    query = input().split(" ")
    for i in range(4):
        adjList[4*c][i*c+cityMap[query[0]]]=adjList[i*c+cityMap[query[1]]][4*c+1]=0

    seen = set()
    neighbors = set()
    distance = list(map(lambda b : 987654321, range(4*c+2)))
    distance[4*c]=0

    neighbors.add(4*c)

    while len(neighbors) > 0:
        lowest = next(iter(neighbors))
        for i in neighbors:
            if distance[lowest]>distance[i]:
                lowest = i
        seen.add(lowest)
        neighbors.remove(lowest)
        for t in adjList[lowest].keys():
            if t not in seen:
                distance[t] = min(distance[t], distance[lowest]+adjList[lowest][t])
                neighbors.add(t)
    print(distance[4*c+1])