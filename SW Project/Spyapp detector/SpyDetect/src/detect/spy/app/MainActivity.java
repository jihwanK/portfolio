package detect.spy.app;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import android.app.Activity;
import android.content.ComponentName;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.widget.Toast;

public class MainActivity extends Activity {

	long start;
	
	boolean isAppFinished = false;
	boolean isVaccineFinished = false;
	boolean isSpyAppFinished = false;
	boolean isDangerFinished = false;
	
	String mSdPath;
	
	File appSource;
	File vaccineSource;
	File spyAppSource;
	File dangerSource;
	
	String appDest;
	String vaccineDest;
	String spyAppDest;
	String dangerDest;
	
	File reportSource;
	String reportDest;
	
	InputStream inBackground;
	InputStream inGarbage;
	InputStream inDivBack;
//	InputStream inSubtitle;
	InputStream inDscLogo;
	InputStream inSubtitle_01;
	InputStream inSubtitle_02;
	InputStream inSubtitle_03;
	InputStream inStartHtml;

	Thread danger;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		
		start = System.currentTimeMillis();
		
		Thread spyapp = new Thread(new DetectSpy(getApplicationContext(), mHandler, "spyapp"));
		Thread vaccine = new Thread(new FindVaccine(getApplicationContext(), mHandler, "vaccine"));
		Thread app = new Thread(new ListedByApp(getApplicationContext(), mHandler, "app"));
		danger = new Thread(new DetectDangerApp(getApplicationContext(), mHandler, "danger"));
				
//		new DetectSpy(getApplicationContext(), mHandler, "spyapp").run();
//		new FindVaccine(getApplicationContext(), mHandler, "vaccine").run();
//		new ListedByApp(getApplicationContext(), mHandler, "app").run();
		
		app.setDaemon(true);
		spyapp.setDaemon(true);
		vaccine.setDaemon(true);
		danger.setDaemon(true);


		app.start();
		spyapp.start();
		vaccine.start();

	}

	Handler mHandler = new Handler() {
		public void handleMessage(Message msg) {
			long end;
			
			if (msg.what == 0) {
				isVaccineFinished = true;
			} else if (msg.what == 1) {
				isAppFinished = true;
				danger.start();
			} else if(msg.what == 2) {
				isSpyAppFinished = true;
			} else if(msg.what == 3) {
				isDangerFinished = true;
			}

			if ((isAppFinished && isVaccineFinished && isSpyAppFinished && isDangerFinished) == true) {
				new MakeReportHTML(getApplicationContext(), "app.xml", "vaccine.xml", "spyapp.xml", "danger.xml", mHandler).run();
				end = System.currentTimeMillis();
//				Toast.makeText(getApplicationContext(), "" + (end - start) / 1000.0, Toast.LENGTH_SHORT).show();
				preMove();
				
				if(moveFiles(appSource, appDest) && moveFiles(spyAppSource, spyAppDest) &&
						moveFiles(vaccineSource, vaccineDest) && moveFiles(dangerSource, dangerDest)) {
					end = System.currentTimeMillis();
//					Toast.makeText(getApplicationContext(), "" + (end - start) / 1000.0, Toast.LENGTH_SHORT).show();
//					getFile(inBackground, "cyber_shield.jpg");
					getFile(inGarbage, "garbage5.png");
//					getFile(inDivBack, "div_back.jpg");
//					getFile(inSubtitle, "subtitle.png");
					getFile(inDscLogo, "dsc.png");
//					getFile(inSubtitle_01, "sub01.png");
//					getFile(inSubtitle_02, "sub02.png");
//					getFile(inSubtitle_03, "sub03.png");
					getFile(inStartHtml, "startReport.html");
					moveFiles(reportSource, reportDest);
				} else 
					Toast.makeText(getApplicationContext(), "파일이동 실패!!!!", Toast.LENGTH_LONG).show();
			}
		}
	};

	private void preMove() {
		String ext = Environment.getExternalStorageState();

		if (ext.equals(Environment.MEDIA_MOUNTED))
			mSdPath = Environment.getExternalStorageDirectory()
					.getAbsolutePath();
		else
			mSdPath = Environment.MEDIA_UNMOUNTED;
		
		File makedir = new File(mSdPath + "/permission");
		makedir.mkdir();
		
		appSource = new File(mSdPath + "/tmp/app.xml");
		vaccineSource = new File(mSdPath + "/tmp/vaccine.xml");
		spyAppSource = new File(mSdPath + "/tmp/spyapp.xml");
		dangerSource = new File(mSdPath + "/tmp/danger.xml");
		
		appDest = mSdPath + "/permission/app.xml";
		vaccineDest = mSdPath + "/permission/vaccine.xml";
		spyAppDest = mSdPath + "/permission/spyapp.xml";
		dangerDest = mSdPath + "/permission/danger.xml";

		reportSource = new File(mSdPath + "/tmp/Report.html");
		reportDest = mSdPath + "/permission/report.html";
		
		inBackground = getResources().openRawResource(R.raw.cyber_shield);
		inGarbage = getResources().openRawResource(R.raw.garbage5);
		inDivBack = getResources().openRawResource(R.raw.div_back);
//		inSubtitle = getResources().openRawResource(R.raw.subtitle);
		inDscLogo = getResources().openRawResource(R.raw.dsc);
		inSubtitle_01 = getResources().openRawResource(R.raw.sub01);
		inSubtitle_02 = getResources().openRawResource(R.raw.sub02);
		inSubtitle_03 = getResources().openRawResource(R.raw.sub03);
		inStartHtml = getResources().openRawResource(R.raw.open_report);
	}
	
	private boolean moveFiles(File source, String dest) {
		boolean result = false;
		
		if((source!=null) && (source.exists())) {
			try {
				FileInputStream fis = new FileInputStream(source);
				FileOutputStream fos = new FileOutputStream(dest);
				
				int readCnt = 0;
				byte[] buffer = new byte[1024];
				while((readCnt = fis.read(buffer, 0, 1024)) != -1) {
					fos.write(buffer, 0, readCnt);
				}
				fos.close();
				fis.close();
			} catch (FileNotFoundException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			result = true;
		} else {
			result = false;
		}
		return result;
	}
	
	public void getFile(InputStream in, String fileName) {
		try {
			
			String ext = Environment.getExternalStorageState();
			
			if (ext.equals(Environment.MEDIA_MOUNTED))
				mSdPath = Environment.getExternalStorageDirectory()
						.getAbsolutePath();
			else
				mSdPath = Environment.MEDIA_UNMOUNTED;
			
			File makedir = new File(mSdPath + "/permission");
			makedir.mkdir();
			
			String dest = mSdPath + "/permission/" + fileName;
			OutputStream out = new FileOutputStream(dest);
			
			int readLen;
			byte buf[] = new byte[1024];
			
			while (true) {
				readLen = in.read(buf);
				if(readLen == -1)
					break;
				
				out.write(buf, 0, readLen);
			}
			
			in.close();
			out.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
//		Toast.makeText(getApplicationContext(), "성공!!!!!!!!!!", Toast.LENGTH_LONG).show();
	}
	
}
