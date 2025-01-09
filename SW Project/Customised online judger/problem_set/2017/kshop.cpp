// Arup Guha
// 8/22/2017
// Solution to 2017 UCF Locals Problem: K Shop

#include <iostream>
#include <cmath>

using namespace std;

// Constants
const double PI = 3.14159265358979;
const long long MOD = 997LL;
const int MAX = 50000;
const int len = (1<<17);

// Globals.
int n;
int* order;
double* cosarr;
double* sinarr;
int* poly;

void fft(double* real, double* img, bool invert);
long long* multiply(int* a, int* b);

int* scale(long long* arr);
int* mypow(int* poly, int exp);

int main() {
    
	// Building order array for FFT.
	order = new int[2];
	order[0] = 0;
	order[1] = 1;
    int orderlen = 2;
    
	// Just iterate building next array from previous.
	while (orderlen != len) {
		int* tmp = new int[orderlen<<1];
		for (int i=0; i<orderlen; i++) {
			tmp[2*i] = order[i];
			tmp[2*i+1] = order[i] + orderlen;
		}
		delete [] order;
		order = tmp;
		orderlen <<= 1;
	}
    
	// Pre-calculate.
	cosarr = new double[len];
	for (int i=0; i<len; i++) cosarr[i] = cos(i*2*PI/len);
	sinarr = new double[len];
	for (int i=0; i<len; i++) sinarr[i] = sin(i*2*PI/len);

    int numCases;
    cin >> numCases;
    
    // Process each case.
    for (int loop=0; loop<numCases; loop++) {

        // Read in the polynomial.
        poly = new int[len];
        for (int i=0; i<len; i++) poly[i] = 0;    
        int n;
        cin >> n;
        for (int i=0; i<n; i++) {
            double price;
            cin >> price;
            poly[(int)(100*price + .1)]++;   
        }
        
        // Read in exponent and number of queries.
        int exp, numQ;
        cin >> exp >> numQ;
        
        // Exponentiate our polynomial.
        int* res = mypow(poly, exp);
        
        // Now handle the queries.
        for (int i=0; i<numQ; i++) {
            double price;
            cin >> price;
            cout << res[(int)(100*price + .1)] << endl;            
        }
        cout << endl;
    
        // Clean up.
        delete [] res;
        if (exp > 1) delete [] poly;
    }
	
    // Clean up.
    delete [] order;
    delete [] cosarr;
    delete [] sinarr;
    return 0;    		
}

// Raises poly to the exp using our MOD and lopping off appropriate terms.
int* mypow(int* poly, int exp) {
    
    // Done.    
    if (exp == 1) return poly;
    
    // Get the time savings here.
    if (exp%2 == 0) {
        int* halfway = mypow(poly, exp/2);
        long long* res = multiply(halfway, halfway);
        if (exp > 2) delete [] halfway;
        return scale(res);    
    }
    
    // Slow way, never runs twice in a row.
    int* rest = mypow(poly, exp-1);
    long long* res = multiply(rest, poly);
    delete [] rest;
    return scale(res);    
}

// Scales the polynomial arr - lops off terms past MAX and does MOD.
int* scale(long long* arr) {
    int* res = new int[len];
    for (int i=0; i<=MAX; i++)    res[i] = (int)(arr[i]%MOD);
    for (int i=MAX+1; i<len; i++) res[i] = 0;
    delete [] arr;
    return res;    
}

void fft(double* real, double* img, bool invert) {

	// Re-order numbers to be in fft ordering for combination.
	double* tmp = new double[len];
	for (int i=0; i<len; i++) tmp[i] = real[order[i]];
	for (int i=0; i<len; i++) real[i] = tmp[i];
    delete [] tmp;
    
	tmp = new double[len];
	for (int i=0; i<len; i++) tmp[i] = img[order[i]];
	for (int i=0; i<len; i++) img[i] = tmp[i];
    delete [] tmp;
    
	// size is the size of each grouping (when we combine up) in fft.
	for (int size=2; size<=len; size<<=1) {

		// Set up angle and halfway pt.
		int half = (size>>1);
		int skip = len/size;
		int sign = !invert ? 1 : -1;

		// i is the starting index for this group, j indicates pairs.
		for (int i=0; i<len; i+=size) {
			double aReal = 1, aImg = 0;
			int index = 0;
			for (int j=0; j<half; j++) {
				double fReal = real[i+j], fImg = img[i+j];
				double sReal = real[i+j+half]*cosarr[index] - img[i+j+half]*sinarr[index];
				double sImg = img[i+j+half]*cosarr[index] + real[i+j+half]*sinarr[index];
				real[i+j] = fReal + sReal;
				img[i+j] = fImg + sImg;
				real[i+j+half] = fReal - sReal;
				img[i+j+half] = fImg - sImg;
				index = (index+sign*skip+len)%len;
			}
		}
	}

	// For inverse transformation, we divide by n (my len).
	if (invert) {
		for (int i=0; i<len; i++) {
			real[i] /= len;
			img[i] /= len;
		}
	}
}

long long* multiply(int* a, int* b) {

	// Copy a.
	double* reala = new double[len];
	for (int i=0; i<len; i++) reala[i] = a[i];
	double* imga = new double[len];
    for (int i=0; i<len; i++) imga[i] = 0.0;
    
	// Copy b.
	double* realb = new double[len];
	for (int i=0; i<len; i++) realb[i] = b[i];
	double* imgb = new double[len];
    for (int i=0; i<len; i++) imgb[i] = 0.0;
    
	// Transform into points.
	fft(reala, imga, false);
	fft(realb, imgb, false);

	// Store product pts here.
	double* realPts = new double[len];
	double* imgPts = new double[len];

	// Multiply points.
	for (int i=0; i<len; i++) {
		realPts[i] = reala[i]*realb[i] - imga[i]*imgb[i];
		imgPts[i] = reala[i]*imgb[i] + realb[i]*imga[i];
	}
    
	// Now, convert these points back to a polynomial.
	fft(realPts, imgPts, true);

	// Finally copy over into a result array without doubles.
	long long* res = new long long[len];
	for (int i=0; i<len; i++)
		res[i] = (long long)(realPts[i]+.5+1e-9);
		
	delete [] reala;
	delete [] imga;
	delete [] realb;
	delete [] imgb;
	delete [] realPts;
	delete [] imgPts;
	
	return res;
}
