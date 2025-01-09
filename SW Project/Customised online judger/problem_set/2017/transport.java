import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map.Entry;
import java.util.PriorityQueue;
import java.util.Scanner;

public class transport {

	private static List<String> modes = Arrays.asList("AIR", "SEA", "RAIL", "TRUCK");

	public static void main(String[] args) {
		try (Scanner in = new Scanner(System.in)) {
			int cases = in.nextInt();
			for (int a = 0; a < cases; a++) {
				int cities = in.nextInt();
				HashMap<String, HashMap<String, Integer>> adjList = new HashMap<>();

				for (int i = 0; i < cities; i++) {
					String city = in.next();
					int transfer = in.nextInt();

					for (String mode : modes) {
						adjList.put(city + mode, new HashMap<>());
						for (String d : modes) {
							adjList.get(city + mode).put(city + d, transfer);
						}
					}

				}

				int routes = in.nextInt();

				for (int i = 0; i < routes; i++) {
					String origin = in.next();
					String dest = in.next();
					String mode = in.next();
					int cost = in.nextInt();
					adjList.get(origin + mode).put(dest + mode, cost);
					adjList.get(dest + mode).put(origin + mode, cost);
				}

				String orig = in.next();
				String dest = in.next();

				adjList.put(orig, new HashMap<>());
				adjList.put(dest, new HashMap<>());
				
				for (String mode : modes) {
					adjList.get(orig).put(orig + mode, 0);
					adjList.get(dest + mode).put(dest, 0);
				}

				HashMap<String, Integer> cityCosts = new HashMap<>();
				addMin(cityCosts,orig, 0);

				HashSet<String> seen = new HashSet<>();

				PriorityQueue<state> q = new PriorityQueue<>();
				q.add(new state(orig, 0));

				while (!q.isEmpty()) {
					state s = q.poll();
					if (!seen.contains(s.city)){
						for (Entry<String,Integer> t: adjList.get(s.city).entrySet()){
							addMin(cityCosts, t.getKey(), cityCosts.get(s.city)+t.getValue());
							q.add(new state(t.getKey(),cityCosts.get(t.getKey())));
						}
						seen.add(s.city);
					}
				}
				
				System.out.println(cityCosts.get(dest));
				
			}

		}
	}

	static void addMin(HashMap<String, Integer> costs, String city, int cost) {
		costs.put(city, costs.containsKey(city) ? Math.min(cost, costs.get(city)) : cost);
	}

	public static class state implements Comparable<state> {
		String city;
		int cost;

		public state(String city, int cost) {
			this.city = city;
			this.cost = cost;
		}

		@Override
		public int compareTo(state o) {
			return cost - o.cost;
		}
	}
}
