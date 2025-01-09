// Arup Guha
// 8/27/2011
// Alternate Solution to 2011 Fall Programming Team Tryout problem: Cutcake

import java.io.*;
import java.util.*;

// Manages information for one vertex.
class vertex {

	public double x;
	public double y;

	public vertex(double my_x, double my_y) {
		x = my_x;
		y = my_y;
	}
	
	public String toString() {
		return "("+x+","+y+")";
	}
}

// Manages information for one side of a polygon.
class edge {

	public vertex u;
	public vertex v;

	public edge(vertex a, vertex b) {
		u = a;
		v = b;
	}

	// Returns the length of this edge.
	public double distance() {
		return Math.sqrt(Math.pow(u.x-v.x,2) + Math.pow(u.y-v.y,2));
	}

	// Returns the point at which the horizontal line y = y_val intersects
	// this edge. If no such intersection exists, null is returned.
	public vertex intersect(int y_val) {

		// Find the minimum and maximum vertices in terms of y value.
		vertex low = u;
		vertex high = v;
		if (u.y > v.y) {
			low = v;
			high = u;
		}

		// Based on the problem statement, no intersection will occur with a horizontal
		// line segment. This return avoids a divide by zero error later.
		if (low.y == high.y)
			return null;

		// The intersection is outside of the bounds of this line segment.
		if (low.y > y_val || high.y < y_val)
			return null;

		// The ratio from the low point to the high point that our intersection lies.
		double ratio = (y_val - low.y)/(high.y - low.y);

		// This is the new x point of intersection. We know the y, already.
		double newx = low.x + ratio*(high.x-low.x);

		return new vertex(newx, y_val);
	}
}

class poly {
	
	public final static boolean DEBUG = false;

	// We will redundantly store the information so that we can access what we want easily.
	public vertex list_v[];
	public edge list_e[];

	public poly(vertex points[]) {

		// Just copy the points.
		list_v = points;

		// Set up the array for edges.
		int len = points.length;
		list_e = new edge[len];

		// Each edge is formed form consecutive pairs of points.
		for (int i=0; i<points.length; i++) {
			list_e[i] = new edge(points[i], points[(i+1)%len]);
		}

	}
	
	// To use for ArrayLists. points must not be empty.
	public poly(ArrayList<vertex> points) {

		// Just copy the points.
		list_v = new vertex[points.size()];
		for (int i=0; i<list_v.length; i++)
			list_v[i] = points.get(i);

		// Set up the array for edges.
		int len = points.size();
		list_e = new edge[len];

		// Each edge is formed form consecutive pairs of points.
		for (int i=0; i<list_e.length; i++) {
			list_e[i] = new edge(list_v[i], list_v[(i+1)%len]);
		}

	}

	// Find the perimeter of this polygon by summing each edge.
	public double perimeter() {

		double sum = 0;
		for (int i=0; i<list_e.length; i++)
			sum += list_e[i].distance();

		return sum;
	}

	// Return the two polygons formed by splitting it with the line y = y_val.
	// If no intersection occurs, the array will store null in index 1 and the
	// original polygon in index 0.
	public poly[] split(int y_val) {

		int[] edge_cut = new int[2];
		vertex[] newpoints = new vertex[2];
		int ptsFound = 0;
		
		// Create the list of vertices for the two polygons. 
		ArrayList<vertex> poly1 = new ArrayList<vertex>();
		ArrayList<vertex> poly2 = new ArrayList<vertex>();
		
		// true means add to poly1, false means add to poly2
		boolean flag = true; 
		boolean hasTwoPolys = false;
		
		// We are setting this vertex in poly1.
		poly1.add(list_v[0]);

		// Loop through each edge.
		for (int i=0; i<list_e.length; i++) {

			// Find the intersection between this edge and the horizontal line.
			vertex temp = list_e[i].intersect(y_val);

			// There was actually an intersection.
			if (temp != null) {
				
				// We've changed over from one poly to another poly.
				flag = !flag;
				hasTwoPolys = true;
				
				// This intersection point is in BOTH polygons.
				poly1.add(temp);
				poly2.add(temp);
				
				if (DEBUG) System.out.println("Added "+temp+" to both.");

			}
			
			// We only add a vertex if we're not on our last iteration.
			if (i<list_e.length-1) {
	
				// Add to the first poly.		
				if (flag) {
				
					poly1.add(list_v[i+1]);
					if (DEBUG) System.out.println("Added "+list_v[i+1]+" to poly1.");
				}
				else {
				
					poly2.add(list_v[i+1]);
					if (DEBUG) System.out.println("Added "+list_v[i+1]+" to poly2.");
				}
			}
		}
		
		// Create the array to return the answers.
		poly[] ans = new poly[2];
		ans[0] = new poly(poly1);
		ans[1] = null;
		
		// Check the case where the polygon wasn't split.
		if (!hasTwoPolys)
			return ans;
			
		// Convert the second polygon and return.
		ans[1] = new poly(poly2);
		return ans;
		
	}
	
	public String toString() {
		String s = "";
		for (int i=0; i<list_v.length; i++)
			s = s +  list_v[i] + " ";
		return s;
	}

}

public class polycake {
	
	public final static boolean DEBUG = false;

	public static void main(String[] args) throws Exception {

		Scanner fin = new Scanner(new File("polycake.in"));
		int numCases = fin.nextInt();
		
		// Loop through the cases.
		for (int i=1; i<=numCases; i++) {
			
			int size = fin.nextInt();
			int y_val = fin.nextInt();
			
			vertex[] list = new vertex[size];
			
			// Read through each vertex in this poly.
			for (int j=0; j<list.length; j++) {
				int x = fin.nextInt();
				int y = fin.nextInt();
				list[j] = new vertex(x,y);
			}
			
			// Create our polygon.
			poly p = new poly(list);
			
			// Split this polygon into two.
			poly[] ans = p.split(y_val);
			double[] perim = new double[2];
			
			// Calculate the perimeter of both.
			for (int j=0; j<2; j++)
				perim[j] = ans[j].perimeter();
			
			// The pinnacle of laziness.
			Arrays.sort(perim);
			
			if (DEBUG) System.out.println(ans[0]);
			if (DEBUG) System.out.println(ans[1]);
			
			// Output the answers.
			System.out.printf("%.3f %.3f\n", perim[0], perim[1]);
		}

		fin.close();
	}
}
