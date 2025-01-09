import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Scanner;
import java.util.stream.IntStream;

public class typing {

	private static String[] keyboard = { 
		"           ", 
		" abcdefghi ", 
		" jklmnopqr ", 
		" stuvwxyz  ", 
		"           " 
	};

	static int[] dx = { 0, 1, 1, 0, -1, -1, -1, 0, 1 };
	static int[] dy = { 0, 0, 1, 1, 1, 0, -1, -1, -1 };
	
	static Map<Character, HashSet<Character>> mapping = new HashMap<>();

	public static void main(String[] args) {

		IntStream.rangeClosed('a', 'z').forEach(c -> mapping.put((char) c, new HashSet<>()));

		for (int i = 0; i < 26; i++) {
			for (int k = 0; k < 9; k++) {
				mapping.get(keyboard[i / 9 + 1].charAt(i % 9 + 1)).add(keyboard[i / 9 + 1 + dy[k]].charAt(i % 9 + 1 + dx[k]));
			}
		}

		try (Scanner in = new Scanner(System.in)) {
			int cases = in.nextInt();

			for (int a = 0; a < cases; a++) {
				String first = in.next();
				String second = in.next();
				
				if (first.equals(second)) {
					System.out.println(1);
				} else if (first.length() != second.length()) {
					System.out.println(3);
				} else {
					System.out.println(checkNeighbors(first, second));
				}
			}
		}
	}

	private static int checkNeighbors(String first, String second) {
		for (int i = 0; i < first.length(); i++) {
			if (!mapping.get(first.charAt(i)).contains(second.charAt(i))) {
				return 3;
			}
		}
		return 2;
	}

}
