import java.util.Scanner;

public class singing {
	public static void main(String[] arg) {
		try (Scanner in = new Scanner(System.in)) {
			int cases = in.nextInt();

			for (int a = 0; a < cases; a++) {
				int tracks = in.nextInt();
				int requests = in.nextInt();

				int last = in.nextInt();

				long total = 0;

				for (int i = 1; i < requests; i++) {
					int next = in.nextInt();
					total += Math.min(tracks - ((next - last - 1) % tracks + tracks) % tracks, ((next - last - 1) % tracks + tracks) % tracks);
					last = next;
				}
				System.out.println(total);

			}
		}
	}
}
