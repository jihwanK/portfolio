import java.io.*;
import java.util.*;


class RowCol {
   public RowCol(int row, int col) {
      this.row = row;
      this.col = col;
   }

   public int row = -1;
   public int col = -1;
};


class search {
   // Set this to 'true' to enable validation of the input file.
   static final boolean VALIDATE = false;

   // Set this to 'true' to enable debug outputs
   static final boolean DEBUG = false;

   // The main method for our search class.
   // It must have a String[] parameter to be recognized by Java runtime, even though we don't use it.
   public static void main(String[] x) throws IOException {

      // Set up our input from the standard input stream
      Scanner sc = new Scanner(System.in);

      // We'll use 'n' for the number of input puzzles, as given in the problem
      int n = sc.nextInt();
      if (DEBUG) System.err.printf("DEBUG: input n=%d%n", n);
      if (VALIDATE) checkMinPuzzles(n);

      // We'll use 'p' to count through the input puzzles as we process them (input and output)
      for (int p = 1; p <= n; ++p) {
         processPuzzle(sc, p);
      }
   }

   static void processPuzzle(Scanner sc, int p) {
      // Go ahead and output the header for the puzzle
      System.out.printf("Word search puzzle #%d:%n", p);

      // Read the row and column (r and c, as in the problem).
      // We don't care about spaces or line endings; Scanner takes care of them.
      // Judging note: Using Scanner, we can't validate the spacing of the input file.
      int r = sc.nextInt();
      if (DEBUG) System.err.printf("DEBUG: r=%d%n", r);
      int c = sc.nextInt();
      if (DEBUG) System.err.printf("DEBUG: c=%d%n", c);
      if (VALIDATE) checkPuzzleSize(p, r, c);

      // Use an array of strings to read each row of the puzzle into a String
      String[] rowstr = new String[r];
      for (int i = 0; i < r; ++i) {
         rowstr[i] = sc.next();
         if (DEBUG) System.err.printf("DEBUG: row %d=[%s]%n", i, rowstr[i]);
         if (VALIDATE) {
            checkRowLength(p, c, i+1, rowstr[i]);
            checkRowUppercase(p, r+1, rowstr[i]);
         }
      }

      // There are only 26 possible starting letters, so map them to the relevant loops
      Map<Character, ArrayList<RowCol>> startingLetterMap = new HashMap<Character, ArrayList<RowCol>>();

      // pre-calculate all the loops - forward and backward for each direction
      fillMap(startingLetterMap, r, c, rowstr);

      // Get the number of search words, 's' as given in the problem
      int s = sc.nextInt();
      if (DEBUG) System.err.printf("DEBUG: s=%d%n", s);
      if (VALIDATE) checkMinSearchWords(p, s);

      // fully process each search word (input, search, and output)
      for (int k = 1; k <= s; ++k) {
         processSearchWord(sc, p, k, r, c, rowstr, startingLetterMap);
      }
      System.out.println();
   }

   static void fillMap(Map<Character, ArrayList<RowCol>> letterMap, int r, int c, String[] rowstr) {
      for (int i = 0; i < r; ++i) {
         for (int j = 0; j < c; ++j) {
            RowCol rc = new RowCol(i + 1, j + 1);
            Character ch = new Character(rowstr[i].charAt(j));
            ArrayList<RowCol> tmpList = letterMap.get(ch);
            if (null == tmpList) {
               tmpList = new ArrayList<RowCol>();
               tmpList.add(rc);
               letterMap.put(ch, tmpList);
            }
            else {
               tmpList.add(rc);
            }
         }
      }
   }

   static void processSearchWord(Scanner sc, int p, int k, int r, int c, String[] rowstr, Map<Character, ArrayList<RowCol>> startMap) {
      // read in the search word
      String w = sc.next();
      if (DEBUG) System.err.printf("DEBUG: word %d=[%s]%n", k, w);
      if (VALIDATE) {
         checkSearchWordUppercase(p, k, w);
         checkSearchWordLength(p, k, w);
         checkSearchWordPalindrome(p, k, w);
         //checkSearchWordConcatenatedPalindromes(p, k, w);
      }

      // for each position (RowCol) that has the starting letter of the word, search in 4 directions
      Character ch = new Character(w.charAt(0));
      ArrayList<RowCol> rcList = startMap.get(ch);
      int ir = -1;
      int ic = -1;
      int iw = -1;
      boolean found[] = new boolean[] { false };

      for (RowCol rc : rcList) {

         // search right
         ir = rc.row - 1;
         ic = rc.col - 1;
         iw = 0;
         while (rowstr[ir].charAt(ic) == w.charAt(iw)) {
            if (DEBUG) System.err.printf("dir=R: ir=%d, ic=%d, iw=%d%n", ir, ic, iw);
            iw += 1;
            if (iw > w.length() - 1) {
               if (foundWord(w, rc.row, rc.col, "R", found)) return;
               break;
            }
            ic += 1;
            if (ic > c - 1) {
               ic = 0;
            }
         }

         // search left
         ir = rc.row - 1;
         ic = rc.col - 1;
         iw = 0;
         while (rowstr[ir].charAt(ic) == w.charAt(iw)) {
            if (DEBUG) System.err.printf("dir=L: ir=%d, ic=%d, iw=%d%n", ir, ic, iw);
            iw += 1;
            if (iw > w.length() - 1) {
               if (foundWord(w, rc.row, rc.col, "L", found)) return;
               break;
            }
            ic += -1;
            if (ic < 0) {
               ic = c - 1;
            }
         }

         // search down
         ir = rc.row - 1;
         ic = rc.col - 1;
         iw = 0;
         while (rowstr[ir].charAt(ic) == w.charAt(iw)) {
            if (DEBUG) System.err.printf("dir=D: ir=%d, ic=%d, iw=%d%n", ir, ic, iw);
            iw += 1;
            if (iw > w.length() - 1) {
               if (foundWord(w, rc.row, rc.col, "D", found)) return;
               break;
            }
            ir += 1;
            if (ir > r - 1) {
               ir = 0;
            }
         }

         // search up
         ir = rc.row - 1;
         ic = rc.col - 1;
         iw = 0;
         while (rowstr[ir].charAt(ic) == w.charAt(iw)) {
            if (DEBUG) System.err.printf("dir=U: ir=%d, ic=%d, iw=%d%n", ir, ic, iw);
            iw += 1;
            if (iw > w.length() - 1) {
               if (foundWord(w, rc.row, rc.col, "U", found)) return;
               break;
            }
            ir += -1;
            if (ir < 0) {
               ir = r - 1;
            }
         }
      }

      if (VALIDATE) {
         if (!found[0]) System.err.printf("ERROR: puzzle %d, word [%s] was not found%n", p, w);
      }

   }

   static boolean foundWord(String w, int r, int c, String dir, boolean[] found) {
      System.out.printf("%s %d %d %s%n", dir, r, c, w);
      if (VALIDATE) {
         if (found[0]) {
            System.err.printf("ERROR: word [%s] was previously found%n", w);
         }
         found[0] = true;
         return false;
      }
      return true;
   }


   // The following are used only for validation of the input.
   // Submitted programs should not need to worry about this.

   static final int MIN_PUZZLES = 1;
   static final int PUZZLE_MINROWS = 3;
   static final int PUZZLE_MAXROWS = 12;
   static final int PUZZLE_MINCOLUMNS = 3;
   static final int PUZZLE_MAXCOLUMNS = 20;
   static final int MIN_SEARCHWORDS = 1;
   static final int SEARCHWORD_MINLENGTH = 3;
   static final int SEARCHWORD_MAXLENGTH = 100;

   static void checkMinPuzzles(int n) {
      if (n < MIN_PUZZLES) {
         System.err.printf("ERROR: number of puzzles too small, not allowed: n = %d%n", n);
         System.exit(1);
      }
   }

   static void checkPuzzleSize(int p, int r, int c) {
      if (r < PUZZLE_MINROWS) {
         System.err.printf("ERROR: Puzzle has less than %d rows, not allowed: puzzle %d r=%d, c=%d%n", PUZZLE_MINROWS, p, r, c);
         System.exit(1);
      }
      if (r > PUZZLE_MAXROWS) {
         System.err.printf("ERROR: Puzzle has more than %d rows, not allowed: puzzle %d r=%d, c=%d%n", PUZZLE_MAXROWS, p, r, c);
         System.exit(1);
      }
      if (c < PUZZLE_MINCOLUMNS) {
         System.err.printf("ERROR: Puzzle has less than %d columns, not allowed: puzzle %d r=%d, c=%d%n", PUZZLE_MINCOLUMNS, p, r, c);
         System.exit(1);
      }
      if (c > PUZZLE_MAXCOLUMNS) {
         System.err.printf("ERROR: Puzzle has more than %d columns, not allowed: puzzle %d r=%d, c=%d%n", PUZZLE_MAXCOLUMNS, p, r, c);
         System.exit(1);
      }
   }

   static void checkRowLength(int p, int c, int rIndex, String rowstr) {
      if (rowstr.length() != c) {
         System.err.printf("ERROR: Puzzle row has less than %d columns, not allowed: puzzle %d row %d = [%s]%n", p, c, rIndex, rowstr);
         System.exit(1);
      }
   }

   static void checkRowUppercase(int p, int rIndex, String rowstr) {
      if (!rowstr.replaceAll("[A-Z]+", "").equals("")) {
         System.err.printf("ERROR: Puzzle row has non-uppercase characters, not allowed: puzzle %d row %d = [%s]%n", p, rIndex, rowstr);
         System.exit(1);
      }
   }

   static void checkMinSearchWords(int p, int s) {
      if (s < MIN_SEARCHWORDS) {
         System.err.printf("ERROR: number of search words too small, not allowed: puzzle %d s = %d%n", p, s);
         System.exit(1);
      }
   }

   static void checkSearchWordUppercase(int p, int k, String w) {
      if (!w.replaceAll("[A-Z]+", "").equals("")) {
         System.err.printf("ERROR: Search word has non-uppercase characters, not allowed: puzzle %d word %d [%s]%n", p, k, w);
         System.exit(1);
      }
   }

   static void checkSearchWordLength(int p, int k, String w) {
      if (w.length() < SEARCHWORD_MINLENGTH) {
         System.err.printf("ERROR: Search word shorter than %d, not allowed: puzzle %d word %d [%s]%n", SEARCHWORD_MINLENGTH, p, k, w);
         System.exit(1);
      }
      if (w.length() > SEARCHWORD_MAXLENGTH) {
         System.err.printf("ERROR: Search word longer than %d, not allowed: puzzle %d word %d [%s]%n", SEARCHWORD_MAXLENGTH, p, k, w);
         System.exit(1);
      }
   }

   static void checkSearchWordPalindrome(int p, int k, String w) {
      String wrev = (new StringBuilder(w)).reverse().toString();
      if (wrev.equals(w)) {
         System.err.printf("ERROR: Search word is palindrome, not allowed: puzzle %d word %d [%s]%n", p, k, w);
         System.exit(1);
      }
   }

};


