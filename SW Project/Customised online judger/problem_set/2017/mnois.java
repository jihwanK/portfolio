import java.util.*;
public class mnois {
    public static int[][] memo;
    public static int[][] lis;
    public static int[] nums;
    public static int[][][] lmemo;
    public static int n;
    public static void main(String[] args) {
        Scanner br = new Scanner(System.in);
        int t = br.nextInt();
        for(int c = 1;c<=t;c++) {
            n = br.nextInt();
            nums = new int[n];
            for(int i = 0;i<n;i++){
                nums[i] = br.nextInt();
            }
            memo = new int[n][n+1];
            for(int i = 0;i<n;i++){
                Arrays.fill(memo[i], -1);
            }
            lmemo = new int[n][n+1][n+1];
            for(int i = 0;i<n;i++){
                for(int j = 0;j<n+1;j++){
                    Arrays.fill(lmemo[i][j], -1);
                }
            }
            lis = new int[n][n];
            for(int i = 0;i<n;i++){
                for(int j = i;j<n;j++){
                    lis[i][j] = lis(i, n, j);
                }
            }
            for(int i = 1;i<=n;i++){
                System.out.print(go(0, i));
                if (i != n){
                    System.out.print(" ");
                }
            }
            System.out.println();
        }
    }

    public static int lis(int pos, int last, int max) {
        if (pos > max) {
            return 0;
        }

        if (lmemo[pos][last][max] != -1){
            return lmemo[pos][last][max];
        }

        int best = lis(pos+1, last, max);
        if (last == n || nums[pos] > nums[last]) {
            best = Math.max(best, lis(pos+1, pos, max)+1);
        }
        return lmemo[pos][last][max] = best;
    }

    public static int go(int pos , int k){
        if (pos >= n) {
            return 0;
        }

        if (memo[pos][k] != -1){
            return memo[pos][k];
        }

        int best = go(pos+1, k);
        for(int i = pos;i<n;i++){
            if (lis[pos][i] >= k) {
                best = Math.max(best, go(i+1, k)+lis[pos][i]);
            }
        }

        return memo[pos][k] = best;
    }
}