// Arup Guha
// 8/4/2017
// Solution to 2017 UCF Locals Problem: K Item Shopping Spree

import java.util.*;
import java.io.*;

public class kshop {

	// Useful constants for this problem - len is lower case because my hackpack FFT code uses it.
	final public static long MOD = 997L;
	final public static int MAX = 50000;
	final public static int len = (1<<17);

	// For FFT.
	public static int[] order;
	public static double[] cos;
	public static double[] sin;

	// Stores the polynomial we exponentiate.
	public static int[] poly;

	public static void main(String[] args) throws Exception {

		// Building order array for FFT.
		order = new int[2];
		order[1] = 1;

		// Just iterate building next array from previous.
		while (order.length != len) {
			int[] tmp = new int[order.length<<1];
			for (int i=0; i<order.length; i++) {
				tmp[2*i] = order[i];
				tmp[2*i+1] = order[i] + order.length;
			}
			order = tmp;
		}

		// Pre-calculate.
		cos = new double[len];
		for (int i=0; i<len; i++) cos[i] = Math.cos(i*2*Math.PI/len);
		sin = new double[len];
		for (int i=0; i<len; i++) sin[i] = Math.sin(i*2*Math.PI/len);

		BufferedReader stdin = new BufferedReader(new InputStreamReader(System.in));
		int numCases = Integer.parseInt(stdin.readLine());

		// Process each case.
		for (int loop=0; loop<numCases; loop++) {

			// Read in the polynomial, adding one to each appropriate coefficient (ie. 1.07 is the x^107 coefficient.)
			int n = Integer.parseInt(stdin.readLine());
			poly = new int[len];
			for (int i=0; i<n; i++)
				poly[(int)(100*Double.parseDouble(stdin.readLine())+.1)]++;

			// Now get queries.
			StringTokenizer tok = new StringTokenizer(stdin.readLine());
			int k = Integer.parseInt(tok.nextToken());
			int numQ = Integer.parseInt(tok.nextToken());

			// Magic polynomial exponentiation =)
			int[] res = exp(poly, k);

			// Store results to queries in StringBuffer.
			StringBuffer sb = new StringBuffer();
			for (int i=0; i<numQ; i++) {
				int target = (int)(100*Double.parseDouble(stdin.readLine())+.1);
				sb.append(res[target]+"\n");
			}

			// Output these queries all at once.
			System.out.println(sb);
		}
	}

	public static void fft(double[] real, double[] img, boolean invert) {

		// Re-order numbers to be in fft ordering for combination.
		double[] tmp = new double[len];
		for (int i=0; i<len; i++)
			tmp[i] = real[order[i]];
		for (int i=0; i<len; i++)
			real[i] = tmp[i];

		tmp = new double[len];
		for (int i=0; i<len; i++)
			tmp[i] = img[order[i]];
		for (int i=0; i<len; i++)
			img[i] = tmp[i];

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
					double sReal = real[i+j+half]*cos[index] - img[i+j+half]*sin[index];
					double sImg = img[i+j+half]*cos[index] + real[i+j+half]*sin[index];
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

	// Calculates polynomial f raised to the power k with the relevant mods for the problem.
	public static int[] exp(int[] f, int k) {

		// Simple base case - note, no scaling needed due to bounds.
		if (k == 1) return f;

		// Time savings here.
		if (k%2 == 0) {
			int[] half = exp(f, k/2);
			return scale(multiply(half,half));
		}

		// Slow odd exponent case.
		int[] rest = exp(f, k-1);
		return scale(multiply(rest, f));
	}

	// Returns the portion of the polynomial res we care about - all coefficients are modded and we lop off anything
	// greater than $500.00.
	public static int[] scale(long[] res) {
		int[] target = new int[res.length];
		for (int i=0; i<=MAX; i++)
			target[i] = (int)(res[i]%MOD);
		return target;
	}

	// Returns the product of polynomials a and b.
	public static long[] multiply(int[] a, int[] b) {

		// Copy a.
		double[] reala = new double[len];
		for (int i=0; i<len; i++) reala[i] = a[i];
		double[] imga = new double[len];

		// Copy b.
		double[] realb = new double[len];
		for (int i=0; i<len; i++) realb[i] = b[i];
		double[] imgb = new double[len];

		// Transform into points.
		fft(reala, imga, false);
		fft(realb, imgb, false);

		// Store product pts here.
		double[] realPts = new double[len];
		double[] imgPts = new double[len];

		// Multiply points.
		for (int i=0; i<len; i++) {
			realPts[i] = reala[i]*realb[i] - imga[i]*imgb[i];
			imgPts[i] = reala[i]*imgb[i] + realb[i]*imga[i];
		}

		// Now, convert these points back to a polynomial.
		fft(realPts, imgPts, true);

		// Finally copy over into a result array without doubles.
		long[] res = new long[len];
		for (int i=0; i<len; i++)
			res[i] = (long)(realPts[i]+.5);
			//res[i] = Math.round(realPts[i]);
		return res;
	}
}