import java.io.*;
import java.net.HttpURLConnection;
import java.net.ConnectException;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.net.URI;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.*;

//import org.apache.http.client.methods.CloseableHttpResponse;
//import org.apache.http.client.methods.HttpGet;
//import org.apache.http.client.utils.URIBuilder;
//import org.apache.http.impl.client.CloseableHttpClient;
//import org.apache.http.impl.client.HttpClients;



interface OnLogReadListener {
    void onLogRead(String log);
}



/**
 * Created by KimDhanHee on 2018-01-05.
 */
 class InputLogFileReader {

    public InputLogFileReader() {
    }

    public List<String[]> readLog(File file) throws IOException {
        List<String[]> logList = new ArrayList<>();

        BufferedReader br = new BufferedReader(new FileReader(file));

        String line;

        while((line = br.readLine()) != null) {
            String[] log = line.split("\t");
            System.out.println(line);
            // if (!filtering.isSizeFilter(log) && filtering.isValidGrid(log))
                logList.add(log);
        }

        return logList;
    }

    public void readLog(File file, OnLogReadListener onLogReadListener) {
        try {
            BufferedReader br = new BufferedReader(new FileReader(file));

            String line;
            while((line = br.readLine()) != null) {
                System.out.println(line);

                //String[] log = line.split("\t");

                   // onLogReadListener.onLogRead(log);
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}


// testMain starts here


public class object{
    

    public static int ary[] = new int[25];
    public static int arycopy[] = new int[25];
    public static BufferedWriter out;

    public static void main(String args[]) throws Exception{
        out = new BufferedWriter(new FileWriter("out.txt"));
    
        Reader a = new Reader();
        InputLogSocketReader r = new InputLogSocketReader(3001, a);


    }

//  public static void request(String type) throws Exception {
//      URIBuilder builder = new URIBuilder();
//      builder.setScheme("http").setHost("165.132.105.40").setPort(8010).setPath("/restart")
//          .setParameter(type, null);
//          
//      URI uri = builder.build();
//      HttpGet httpget = new HttpGet(uri);
//      System.out.println(httpget.getURI());
//      
//      CloseableHttpClient httpclient = HttpClients.createDefault();
//      CloseableHttpResponse response = null;
//
//      try {
//          response = httpclient.execute(httpget);
//      } catch (IOException e) {
//              //handle this IOException properly in the future
//      } catch (Exception e) {
//              //handle this IOException properly in the future
//      }
//
//      
//  }
}
class Reader implements OnLogReadListener{
    public void onLogRead(String log){
		
		String str[] = log.split("\t");
        System.out.println(log);
		// System.out.println(str.length + '\n');
		// System.out.println(str.length + " " + str[0] + '\n');
		// if(str.length == 13) {
		// 	System.out.println(str[0] + ',' +
		// 					   str[1] + ',' +
		// 					   Integer.toString(Integer.parseInt(str[3]) - 192168020) + ',' +
		// 					   //str[3] + ',' +
		// 					   str[4] + ',' +
		// 					   str[5] + ',' +
		// 					   str[6] + ',' +
		// 					   str[7] + ',' +
		// 					   str[8] + ',' +
		// 					   str[9] + ',' +
		// 					   str[10] + ',' +
		// 					   str[11]
		// 					   );
		// }
        try {
			// if(str.length == 13) {
			// 	testMain.out.write(str[0] + ',' +
			// 				   str[1] + ',' +
			// 				   Integer.toString(Integer.parseInt(str[3]) - 192168020) + ',' +
			// 				   //str[3] + ',' +
			// 				   str[4] + ',' +
			// 				   str[5] + ',' +
			// 				   str[6] + ',' +
			// 				   str[7] + ',' +
			// 				   str[8] + ',' +
			// 				   str[9] + ',' +
			// 				   str[10] + ',' +
			// 				   str[11] + '\n'
			// 				   );
			// }
            testMain.out.write(log+'\n');
            // testMain.out.flush();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        
    
//      System.out.println("camera - "+str[2]);
//      testMain.ary[Integer.parseInt(log[2])]++;
    }

}
/**
 * Created by KimDhanHee on 2018-03-23.
 */
class InputLogSocketReader implements Runnable {
    private int serverPort;
    private ServerSocket serverSocket;
    private boolean isStopped;
    private Thread runningThread;
    private ExecutorService threadPool;

    private OnLogReadListener onLogReadListener;

    public InputLogSocketReader(int port, OnLogReadListener onLogReadListener) {
        this.onLogReadListener = onLogReadListener;
        this.serverPort = port;
        this.isStopped = false;

        new Thread(this).start();
    }

    @Override
    public void run() {
        synchronized (this) {
            this.runningThread = Thread.currentThread();
        }
        if (serverSocket == null || serverSocket.isClosed()) openServerSocket();

        this.threadPool = Executors.newCachedThreadPool();
        int n=0;
        while (!isStopped()) {
            Socket clientSocket = null;
            try {
                clientSocket = serverSocket.accept();
   
            } catch (IOException e) {
                e.printStackTrace();
                if (isStopped()) {
                    System.out.println("Server Stopped");
                    return;
                }
                throw new RuntimeException("Error accepting client connection", e);
            } catch (Exception e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
            this.threadPool.execute(new ConnectionWrap(clientSocket, onLogReadListener));
            // System.out.println(((ThreadPoolExecutor) threadPool).getPoolSize());
        }
        this.threadPool.shutdown();
        System.out.println("Server Stopped");
    }

    private synchronized boolean isStopped() {
        return this.isStopped;
    }

    private synchronized void stop() {
        this.isStopped = true;
        try {
            this.serverSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void openServerSocket() {
        try {
            this.serverSocket = new ServerSocket(this.serverPort);
            System.out.println("open server on port " + this.serverPort);
        } catch (IOException e) {
            throw new RuntimeException("Cannot open port " + this.serverPort, e);
        }
    }
}

class ConnectionWrap implements Runnable {
    private Socket socket;
    private OnLogReadListener onLogReadListener;

    public ConnectionWrap(Socket socket, OnLogReadListener onLogReadListener) {
        this.socket = socket;
        try {
            this.socket.setSoTimeout(1000 * 60);
        } catch (SocketException e) {
            // e.printStackTrace();
        }
        this.onLogReadListener = onLogReadListener;
    }

    @Override
    public void run() {
        try {
            BufferedReader brIn = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            String line;
            while ((line = brIn.readLine()) != null) {
               //  System.out.println(line);
                onLogReadListener.onLogRead(line);
            }

            brIn.close();
        } catch (IOException e) {
            // e.printStackTrace();
        } finally {
            try {
                // System.out.println("socket" + socket.getLocalPort() + " close");
                socket.close();
            } catch (IOException e) {
                // e.printStackTrace();
            }
        }
    }
}