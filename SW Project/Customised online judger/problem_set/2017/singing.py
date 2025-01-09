cases = int(input())
for a in range(cases):
    tracks = int(input().split(" ")[0])
    requests = input().split(" ")
    last = int(requests[0])
    total = 0
    for i in requests[1:]:
        next = int(i)
        total += min(tracks - ((next - last - 1) % tracks + tracks) % tracks, ((next - last - 1) % tracks + tracks) % tracks)
        last = next
    print(total)