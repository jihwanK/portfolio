import java.util.Scanner;

public class darts {
	public static void main(String[] args) {
		try (Scanner in = new Scanner(System.in)) {
			int cases = in.nextInt();
			for (int a = 0; a < cases; a++) {
				int w = in.nextInt(), b = in.nextInt(), d = in.nextInt(), s = in.nextInt();
				
				int throwCount = in.nextInt();
				int score = 0;
				for (int i = 0; i < throwCount; i++){
					double x = in.nextDouble(), y = in.nextDouble();
					double r = Math.sqrt(x*x+y*y);
					double theta = Math.atan2(y, x);
					if (theta < 0){
						theta += 2.0*Math.PI;
					}
					int wedge = (int)(theta/(2.0*Math.PI)*w)+1;
					
					if (r < b){
						score+=50;
					}
					else if(r < d){
						score += wedge*2;
					}else if(r < s){
						score += wedge;
					}
					
				}
				System.out.println(score);
			}
		}
	}
}
