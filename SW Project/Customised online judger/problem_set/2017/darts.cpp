// Arup Guha
// 9/1/2017
// Solution to 2017 UCF Locals Problem: Darts

#include <iostream>
#include <cmath>

using namespace std;

int points(double radii[], int n, double x, double y);

int main() {

    int numCases;
    cin >> numCases;

    // Process each case.
    for (int loop=0; loop<numCases; loop++) {

        // Read stuff in.
        int n, items;
        cin >> n;
        double radii[3], x, y;
        cin >> radii[0] >> radii[1] >> radii[2];
        cin >> items;

        // Add up each dart.
        int score = 0;
        for (int i=0; i<items; i++) {
            cin >> x >> y;
            score += points(radii, n, x,y);
        }

        // Print out the result.
        cout << score << endl;
    }

	return 0;
}

int points(double radii[], int n, double x, double y) {

    // Convert to polar form.
    double mag = sqrt(x*x+y*y);
    double angle = atan2(y,x);

    // Update angle and find base points.
    if (angle < 0) angle += 2*M_PI;
    int basePts = (int)((n*angle)/(2*M_PI) + 1e-9);
    basePts++;

    // Find which concentric circle we're in.
    if (mag < radii[0]) return 50;
    else if (mag < radii[1]) return 2*basePts;
    else if (mag <= radii[2]) return basePts;
    return 0;
}
