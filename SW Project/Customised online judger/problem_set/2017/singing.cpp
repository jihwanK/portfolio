// Arup Guha
// 8/16/2017
// Solution to 2017 UCF Locals Problem: Singin' in the Rain

#include <iostream>

using namespace std;

int min(int a, int b);

int main() {

    long long n;
    int numCases, len, cur, next;
    cin >> numCases;

    // Process each case.
    for (int loop=0; loop<numCases; loop++) {

        // Tracks and seq length.
        cin >> n >> len;

        // Initialize and get first track.
        long long res = 0;
        cin >> cur;

        // Process the rest.
        for (int i=0; i<len-1; i++) {

            // Get forward difference.
            cin >> next;
            int diff = next - cur - 1;
            if (diff < 0) diff += n;

            // Take the best of both directions.
            res += min(diff, n-diff);

            // Update current track.
            cur = next;
        }

        cout << res << endl;
    }
}

int min(int a, int b) {
    return a < b ? a : b;
}
