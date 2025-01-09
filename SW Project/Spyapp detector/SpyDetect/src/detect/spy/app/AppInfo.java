package detect.spy.app;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.HashMap;
import java.util.List;
import java.util.Scanner;
import java.util.StringTokenizer;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.content.pm.PackageManager.NameNotFoundException;
import android.os.Environment;
import android.os.Handler;
import android.util.Log;

public abstract class AppInfo {

	protected Context context;

	protected String mSdPath;

	protected String importantPerm;
	protected String mustbeMalignantPerm;

	protected DocumentBuilderFactory docFactory;
	protected DocumentBuilder docBuilder;
	protected Document doc;
	protected Element rootElement;

	protected List<ApplicationInfo> packages;
	protected ArrayList<String> Items;
	protected ArrayList<String> malPerm;
	protected HashMap<String, String> spyName;
	protected HashMap<String, String> vaccine;
	protected HashMap<String, String> security;
	
	protected Handler mHandler;

	protected String flag;
	
	protected String myName;
	protected String myLabel;

	public AppInfo(Context context, Handler handler, String flag) {
		this.context = context;
		this.mHandler = handler;
		this.flag = flag;
		
		PackageManager pm = context.getPackageManager();
		myName = context.getApplicationInfo().packageName;
		myLabel = context.getApplicationInfo().loadLabel(pm).toString();

		String ext = Environment.getExternalStorageState();

		if (ext.equals(Environment.MEDIA_MOUNTED))
			mSdPath = Environment.getExternalStorageDirectory()
					.getAbsolutePath();
		else
			mSdPath = Environment.MEDIA_UNMOUNTED;
	}

	/*
	 * xml 파일 형식으로 저장 파일 이름은 flag 형식으로 구현 DOM 파서를 이용해 바꿔줌
	 */

	protected void saveFileExternalMemory() {
		File makedir = new File(mSdPath + "/tmp");
		makedir.mkdir();

		File file = new File(mSdPath + "/tmp/" + flag + ".xml");

		try {

			TransformerFactory transformerFactory = TransformerFactory
					.newInstance();
			Transformer transformer = transformerFactory.newTransformer();

			transformer.setOutputProperty(OutputKeys.ENCODING, "utf-8");
			transformer.setOutputProperty(OutputKeys.INDENT, "yes");
			DOMSource source = new DOMSource(doc);

			StreamResult result = new StreamResult(new FileOutputStream(file));

			transformer.transform(source, result);

		} catch (FileNotFoundException e) {
			Log.e("error", "file not found");
		} catch (SecurityException e) {
			Log.e("error", "security exception occured");
		} catch (Exception e) {
			Log.e("error", e.getMessage());
		}
	}

	// 악성 퍼미션 불러오기
	protected void getMalignantPerm() {
		malPerm = new ArrayList<String>();
		try {
			InputStream in = context.getResources().openRawResource(
					R.raw.malperm);
			// InputStream in = context.getAssets().open("malperm.txt");
			Scanner scan = new Scanner(in);
			String str;

			while (scan.hasNext()) {
				str = scan.nextLine();
				malPerm.add(str);
			}
			scan.close();
			in.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		mustbeMalignantPerm = malPerm.get(0);
	}
	
	//스파이 앱 명칭 불러오기
	protected void getSpyName() {
		spyName = new HashMap<String, String>();
		try {
			InputStream in = context.getResources().openRawResource(
					R.raw.spyname);
			// InputStream in = context.getAssets().open("spyname.txt");
			Scanner scan = new Scanner(in);
			String str;

			while (scan.hasNext()) {
				str = scan.nextLine();
				String spyname;
				String spypack;
				String spypack2;
				
				StringTokenizer tokened = new StringTokenizer(str, "\t");
				spyname = tokened.nextToken();
				spypack = tokened.nextToken();
				
				if(tokened.hasMoreTokens()) {
					spypack2 = tokened.nextToken();
					spyName.put(spypack, spyname);
					spyName.put(spypack2, spyname);
				} else
					spyName.put(spypack, spyname);
			}
			scan.close();
			in.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	protected void getVaccine() {
		vaccine = new HashMap<String, String>();
		try {
			InputStream in = context.getResources().openRawResource(R.raw.vaccine);
			Scanner scan = new Scanner(in);
			String str;

			while (scan.hasNext()) {
				str = scan.nextLine();
				String vaccinename;
				String vaccinepack;
				
				StringTokenizer tokened = new StringTokenizer(str, "\t");
				vaccinename = tokened.nextToken();
				vaccinepack = tokened.nextToken();
				
				vaccine.put(vaccinepack, vaccinename);
			}
			scan.close();
			in.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	protected void getSecurity() {
		security = new HashMap<String, String>();
		try {
			InputStream in = context.getResources().openRawResource(R.raw.security);

			Scanner scan = new Scanner(in);
			String str;

			while (scan.hasNext()) {
				str = scan.nextLine();
				String securityname;
				String securitypack;
				
				StringTokenizer tokened = new StringTokenizer(str, "\t");
				securityname = tokened.nextToken();
				securitypack = tokened.nextToken();
				
				security.put(securitypack, securityname);
			}
			scan.close();
			in.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	
	
	
	protected String getInstalledDate(String packageName) {
		long installed = 0;

		try {
			PackageManager pm = context.getPackageManager();
			installed = pm.getPackageInfo(packageName, 0).firstInstallTime;
		} catch (NameNotFoundException e) {
			e.printStackTrace();
		}

		return getDate(installed);
	}

	protected String getDate(long datetime) {
		DateFormat formatter = new SimpleDateFormat("yy.MM.dd.");

		Calendar calendar = Calendar.getInstance();
		calendar.setTimeInMillis(datetime);
		String strDate = formatter.format(calendar.getTime());

		return "\'"+strDate;
	}
	
//
//	protected abstract void startCreateXml();
//
//	protected abstract void setAppsList();
//
//	protected abstract void setPermissionList(String name, Element app);

}
