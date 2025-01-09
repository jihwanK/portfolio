// Arup Guha
// 9/1/2017
// Solution to 2017 UCF Locals Problem: Editor Navigation

#include <iostream>
#include <queue>

using namespace std;

int n;
int* linelen;

int bfs(int s, int e);
int up(int cur);
int down(int cur);
int left(int cur);
int right(int cur);

int main() {

	int numCases;
	cin >> numCases;

    // Process each case.
    for (int loop=0; loop<numCases; loop++) {

        // Get text information.
        cin >> n;
        linelen = new int[n];
        int start, end, x, y;
        for (int i=0; i<n; i++) cin >> linelen[i];

        // Get search starting and ending points. Make rows 0 based.
        cin >> x >> y;
        start = 81*(x-1) + y;
        cin >> x >> y;
        end = 81*(x-1) + y;

        // Print the shortest distance using a bfs.
        cout << bfs(start, end) << endl;
	}
}

int bfs(int s, int e) {

    // Usual BFS setup.
    queue <int> q;
    int dist[121*81];
    for (int i=0; i<121*81; i++)
        dist[i] = -1;
    q.push(s);
    dist[s] = 0;

    // Run till there are no more reachable places.
    while (q.size() > 0) {

        // Get next item.
        int cur = q.front();
        q.pop();

        // Ta da - we got there!
        if (cur == e) return dist[e];

        // Get each next candidate.
        int next[4];
        next[0] = up(cur);
        next[1] = down(cur);
        next[2] = left(cur);
        next[3] = right(cur);

        // Try enqueing each.
        for (int i=0; i<4; i++) {

            // Skip previously visited squares.
            if (dist[next[i]] != -1) continue;

            // New place, add it and mark distance.
            q.push(next[i]);
            dist[next[i]] = dist[cur] + 1;
        }
    }

    // We know we'll always get there...so this will never trigger.
    return -1;
}

// Returns the location we get to if we go up from cur.
int up(int cur) {

    // Can't go up from the first row.
    if (cur/81 == 0) return cur;

    // Otherwise, we go up...any maybe to the left some...
    int x = cur/81-1;
    int y = linelen[x] < cur%81 ? linelen[x] : cur%81;
    return 81*x+y;
}

// Returns the location we get to if we go down from cur.
int down(int cur) {

    // Can't go down from the bottom row.
    if (cur/81 == n-1) return cur;

    // We go down...and maybe to the left some.
    int x = cur/81+1;
    int y = linelen[x] < cur%81 ? linelen[x] : cur%81;
    return 81*x+y;
}

// Returns the location we get to if we go left from cur.
int left(int cur) {

    // We're stuck at the top left...
    if (cur == 0) return cur;
    int x,y;

    // We can move left.
    if (cur%81 > 0) {
        x = cur/81;
        y = cur%81 - 1;
    }

    // Funny wrap up to the right case.
    else {
        x = cur/81 - 1;
        y = linelen[x];
    }
    return 81*x+y;
}

// Returns the location we get to if we go right from cur.
int right(int cur) {

    // Can't do it from the last char in the file.
    if (cur/81 == n-1 && cur%81 == linelen[n-1]) return cur;
    int x,y;

    // There's room to move right on this row.
    if (cur%81 < linelen[cur/81]) {
        x = cur/81;
        y = cur%81 + 1;
    }

    // We advance to the left end of the next row.
    else {
        x = cur/81 + 1;
        y = 0;
    }
    return 81*x+y;
}
