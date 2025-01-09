/**
 * editor.java
 * Solution for 'Editor Navigation'
 * 2017 UCF Local Programming Contest
 * C Gouge
 */
import java.io.*;
import java.util.*;

class editor {

   // define a very large number to initialize distance values
   static final int oo = (int)1e9;

   // a utility class to help putting pairs of values in a queue
   class position {
      public int r = 1;
      public int c = 0;

      public position(int r, int c) {
         this.r = r;
         this.c = c;
      }

      public boolean equals(position other) {
         if (this.r == other.r && this.c == other.c) return true;
         return false;
      }

      public String toString() {
         return "(" + this.r + "," + this.c + ")";
      }

      // get only valid neighbor positions based on arrow keys;
      // at most 4 and possibly less than 4 depending on the row.
      public ArrayList<position> getValidNeighbors(int f, int[] s) {
         ArrayList<position> n = new ArrayList<position>();
         // left neighbor:
         // if before first char, and not on first line, neighbor is end of previous line
         // otherwise just back one char
         if (this.c == 0) {
            if (this.r > 1) {
               n.add(new position(this.r - 1, s[this.r - 1]));
            }
         }
         else {
            n.add(new position(this.r, this.c - 1));
         }
         // right neighbor:
         // if after last char, and not on last line, neighbor is beginning of next line
         // otherwise just forward one char
         if (this.c == s[this.r]) {
            if (this.r < f) {
               n.add(new position(this.r + 1, 0));
            }
         }
         else {
            n.add(new position(this.r, this.c + 1));
         }
         // up neighbor:
         // can't go up if on the first line
         // up is the previous line, either the same position or the line length
         if (this.r > 1) {
            position p = new position(this.r - 1, this.c);
            if (p.c > s[p.r]) {
               p.c = s[p.r];
            }
            n.add(p);;
         }
         // down neighbor:
         // can't go down if on the last line
         // down is the next line, either the same position or the line length
         if (this.r < f) {
            position p = new position(this.r + 1, this.c);
            if (p.c > s[p.r]) {
               p.c = s[p.r];
            }
            n.add(p);;
         }
         return n;
      }
   };

   // all the work is in the constructor because we need a non-static instance
   editor() throws Exception {
      Scanner sc = new Scanner(System.in);

      // get the number of scenarios in the input
      int numScenarios = sc.nextInt();
      for (int t=1; t <= numScenarios; ++t) {

         // allocate data structures and read all the input for a scenario
         int f = sc.nextInt();
         int[] s = new int[f+1];
         int smax = 0;
         for (int i=1; i <= f; ++i) {
            s[i] = sc.nextInt();
            if (s[i] > smax) smax = s[i];
         }
         position cursor = new position(sc.nextInt(), sc.nextInt());
         position mistake = new position(sc.nextInt(), sc.nextInt());

         // bfs setup
         boolean[][] visited = new boolean[f + 1][smax + 1];
         for (int i=1; i <= f; ++i) {
            for (int j=0; j <= smax; ++j) {
               visited[i][j] = false;
            }
         }
         int[][] distance = new int[f + 1][smax + 1];
         for (int i=1; i <= f; ++i) {
            for (int j=0; j <= smax; ++j) {
               distance[i][j] = oo;
            }
         }

         // queue for bfs (breadth-first search algorithm)
         ArrayList<position> q = new ArrayList<position>();

         // start bfs
         visited[cursor.r][cursor.c] = true;
         q.add(cursor);;
         distance[cursor.r][cursor.c] = 0;

         while (!q.isEmpty()) {
            position current = q.remove(0);
            if (current.equals(mistake)) {
               break;
            }
            for (position neighbor : current.getValidNeighbors(f, s)) {
               if (!visited[neighbor.r][neighbor.c]) {
                  visited[neighbor.r][neighbor.c] = true;
                  q.add(neighbor);
                  distance[neighbor.r][neighbor.c] = 1 + distance[current.r][current.c];
               }
            }
         }

         // output distance (number of keypresses)
         System.out.printf("%d%n", distance[mistake.r][mistake.c]);
      }
   }

   public static void main(String[] args) throws Exception  {
      new editor();
   }

};
