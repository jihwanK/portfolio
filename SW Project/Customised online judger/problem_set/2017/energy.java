import java.util.Scanner;

public class energy {
	public static void main(String[] args) {
		
		try (Scanner in = new Scanner(System.in)) {
			
			int first = in.nextInt();
			int post = in.nextInt();
			int n = in.nextInt();

			for (int i = 0; i < n; i++) {
				int consumption = in.nextInt();

				if (consumption > 1000) {
					System.out.println(consumption + " " + (1000 * first + (consumption - 1000) * post));
				} else {
					System.out.println(consumption + " " + (first * consumption));
				}
			}
		}
	}
}
