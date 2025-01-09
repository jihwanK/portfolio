// Arup Guha
// 8/17/2017
// Solution to 2017 UCF Locals Problem: Rotating Cards

#include <iostream>
#include <cmath>

using namespace std;

class bit {
    
    public:
        bit(int n);
        ~bit();
        void add(int index, long long value);
        long long sum(int index);
        long long sum(int low, int high);
    private:
        long long* cumfreq;
        int n;
};

int lowestOneBit(int n);

int main() {

    int numCases;
    cin >> numCases;
    
    // Process each case.
    for (int loop=0; loop<numCases; loop++) {
        
        // Read in the input, store inverse look up.
        int n;
        cin >> n;
        int* list = new int[n];
        int* rev = new int[n+1];
        for (int i=0; i<n; i++) {
            cin >> list[i];
            rev[list[i]] = i+1;    
        }    
        
        // Set up my bit for quick queries and edits.
        bit mybit(n);
        for (int i=1; i<=n; i++)
        mybit.add(i, list[i-1]);
        
        // Set up initial values.
        long long res = 0;
        long long left = ((long long)n)*(n+1)/2;
        int cur = 1;
        
        // Go through each card.
        for (int i=1; i<=n; i++) {
            
            // Get next interval to jump.
            int next = rev[i];
            int low =  min(cur, next);
            int high = max(cur, next);
            
            // Add in the lower cost (of going up or down).
            long long cost = mybit.sum(low,high-1);
            res += min(cost, left-cost);
            
            // Bookkeeping...
            left -= list[next-1];
            mybit.add(next, -list[next-1]);
            cur = next;
        }
        
        // Ta da!
        cout << res << endl;
    }
    
    return 0;
}

int lowestOneBit(int n) {
    if (n <= 0) return -1;
    int val = 1;
    while ((n & val) == 0) val <<= 1;
    return val;
}

// Here is the Binary Index Tree/Fenwick Tree...
bit::bit(int myn) {
	int size = 1;
	while (size < myn) size <<= 1;
	n = size;
	cumfreq = new long long[n+1];
	for (int i=0; i<=n; i++) cumfreq[i] = 0;
}

bit::~bit() {
    delete [] cumfreq;    
}
void bit::add(int index, long long value) {
	while (index < n+1) {
		cumfreq[index] += value;
		index += lowestOneBit(index);
	}
}

long long bit::sum(int index) {
	long long ans = 0;
	while (index > 0) {
		ans += cumfreq[index];
		index -= lowestOneBit(index);
	}
	return ans;
}

long long bit::sum(int low, int high) {
	return sum(high) - sum(low-1);
}
