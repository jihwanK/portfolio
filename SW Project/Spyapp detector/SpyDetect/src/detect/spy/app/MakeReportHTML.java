package detect.spy.app;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Locale;
import java.util.Scanner;
import java.util.Set;
import java.util.StringTokenizer;
import java.util.TreeSet;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import android.app.KeyguardManager;
import android.bluetooth.BluetoothAdapter;
import android.content.Context;
import android.location.LocationManager;
import android.net.wifi.WifiManager;
import android.nfc.NfcAdapter;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.provider.Settings;
import android.provider.Settings.SettingNotFoundException;
import android.telephony.PhoneNumberUtils;
import android.telephony.TelephonyManager;
import android.util.Log;
import android.widget.Toast;

public class MakeReportHTML implements Runnable {

	private static class SortedApp implements Comparable<SortedApp> {
		private String appName;
		private String packName;
		private double appPercent;

		SortedApp(String appName, String packName, String strAppPercent) {

			this.appPercent = Double.parseDouble(strAppPercent);
			this.appName = appName;
			this.packName = packName;
		}

		public String toString() {
			return appName + " : " + appPercent;
		}

		public int compareTo(SortedApp sa) {
			// TODO Auto-generated method stub

			if (appPercent > sa.appPercent) {
				return -1;
			} else if (appPercent < sa.appPercent) {
				return 1;
			} else {
				return 1;
			}
		}

		public String getAppName() {
			return appName;
		}

		public String getPackName() {
			return packName;
		}

		public double getAppPercent() {
			return appPercent;
		}
	}

//	private TreeSet<SortedApp> sortedList = new TreeSet<SortedApp>();
	private TreeSet<SortedApp> appSet = new TreeSet<SortedApp>();
//	private TreeSet<String> vaccineSet = new TreeSet<String>();
	private HashMap<String, String> descriptionMalPerm = new HashMap<String, String>();
	private HashMap<String, String> deviceName = new HashMap<String, String>();

	protected Context context;

	private String mSdPath;
	private String appFile;
	private String vaccineFile;
	private String spyappFile;
	private String dangerFile;

	protected DocumentBuilderFactory docFactory;
	protected DocumentBuilder docBuilder;
	protected Document docApp;
	protected Document docVaccine;
	protected Document docSpy;
	protected Element rootElement;

	private File app;
	private File vaccine;
	private File spyapp;
	private File danger;

	private FileWriter fWriter;
	private BufferedWriter writer;

	private Handler mHandler;
	
	int numOfDangerApp = 0;
	int numOfSpyApp = 0;
	int numOfVaccineApp = 0;
	int numOfSecuritySetting = 0;
	
	private String screenLockSetting;
	private String nfcSetting;
	private String bluetoothSetting;
	private String wifiSetting;
	private String gpsSetting;
	private String unknownSourceSetting;
	

	public MakeReportHTML(Context context, String appFile, String vaccineFile,
			String spyappFile, String dangerFile, Handler handler) {
		this.context = context;
		this.appFile = appFile;
		this.vaccineFile = vaccineFile;
		this.spyappFile = spyappFile;
		this.dangerFile = dangerFile;
		mHandler = handler;
	}

	void startWriteHTML() {

		String ext = Environment.getExternalStorageState();

		if (ext.equals(Environment.MEDIA_MOUNTED))
			mSdPath = Environment.getExternalStorageDirectory()
					.getAbsolutePath();
		else
			mSdPath = Environment.MEDIA_UNMOUNTED;

		app = new File(mSdPath + "/tmp/" + appFile);
		vaccine = new File(mSdPath + "/tmp/" + vaccineFile);
		spyapp = new File(mSdPath + "/tmp/" + spyappFile);
		danger = new File(mSdPath + "/tmp/" + dangerFile);

		try {
			fWriter = new FileWriter(mSdPath + "/tmp/Report.html");
			writer = new BufferedWriter(fWriter);

			writer.write("<!DOCTYPE html><html>	<head><meta charset=\"utf-8\"><title>REPORT</title>"
					+ "<style> .malignant { color : blue; }	a:link { color : black; } .app_malignant { color: orange; } .perm { padding-left : 30px; } .pack { padding-left : 30px; } "
					+ "#header1 { position : fixed; width : 100%; height : 33%; border-bottom : 2px solid #cccccc; } "
					+ "#content { width : 950px; height: 100%; margin: 0 auto; } "
					+ "#malignant_permission { position : fixed; width : auto; margin-left : 50%; height : auto; color : blue; font-size : 12px; }"
					+ ".high { color : darkred; } .low { color : salmon; } "
					+ "#deviceInfo { font-size : 16px; width : 780px; text-align : center; }"
					+ "body {  }"
					+ "#contentBriefInfo { width : 780px; text-align : center; }"
					+ "th { background-color : #cccccc; }" +
					"#dangerapp { width : 780px; text-align : center; }" +
					"#vaccine { width : 780px; text-align : center; }" +
					"#spyapp { width : 780px; text-align : center; }" +
					"#securitySetting { width : 780px; text-align : center; }" +
					"#appname { width : 28%; } #packname { width : 44%; } " +
					"#date { width : 11%; } #danger { width : 11%; }" +
					"#classification {  width : 11%; }" +
					"#hypertext { border-left-width : 0px; }" +
					"#score { border-right-width : 0px; }" +
					"img { border : 0 }" +
					"#startReport {  }" +
					"#detailedInfo {  }" +
					"#subtitle { width : 100%; border-collapse : collapse; }" +
					"#header, #footer { height : 35px; }" +
					"" +
					"#side { width : 35px; }" +
					"#header > #side { background-color : #39639d; }" +
					"#header > #main { background-color : #7592bb; }" +
					"#contentBody > #side { background-color : #dcdcdc; }" +
					"#contentBody > #main { background-color : white; }" +
					"#footer > #side { background-color : #2da2bf; }" +
					"#footer > #main { background-color : #6cbed2; }" +
					"#mainTitle { border: 3px solid black; margin: auto; width: 680px; font-weight: bold; font-size: 40px; font-family : \"HY������M\"; padding-top: 10px; padding-bottom: 10px; text-align: center;}" +
					"#contentApp { padding: 20px; }" +
					"#box { display : inline-block; width : 23px; height : 23px; border : 2px solid black; }" +
					"#sub { width : 100%; padding : 5px; }" +
					"#detailedInfo h2 { margin-left : 25px; }"
					+ "</style>" +
					"<script type=\"text/javascript\">" +
					"function delfile(pro_name){ " +
					"if(deletePopup()) {" +
					"var path = \"C:\\\\Security\\\\Del_show \" + pro_name;" +
					"var WshShell = new ActiveXObject(\"WScript.Shell\"); WshShell.Run(path, 1, false);" +
					"document.getElementById(pro_name).bgColor = \"#87C8F8\";" +
					"} }" +
					"function deletePopup() {" +
					"if(confirm(\"������ �����Ͻðڽ��ϱ�?\")) {" +
					"return true; }" +
					"else {" +
					"return false; }" +
					"}" +
					"</script></head><body>" +
					"<div id=\"content\">" +
					"<table id=\"subtitle\">" +
					"<tr id=\"header\"><td id=\"side\"> </td><td id=\"main\"> </td><td id=\"side\"> </td></tr>" +
					"<tr id=\"contentBody\"><td id=\"side\"> </td><td id=\"main\"><img src=\"dsc.png\" style=\"width: 300px; margin-top: 10px;\">" +
					"<div id=\"contentApp\">");

			docFactory = DocumentBuilderFactory.newInstance();
			docBuilder = docFactory.newDocumentBuilder();

		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (ParserConfigurationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	void printCheckDate() {
		try {
			writer.write("<div><h1><div id=\"box\"> </div>&nbsp; �� �� : " + getDate() + "</h1></div><br>");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	void printDeviceInfo() {
		TelephonyManager telephony = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
		setDeviceNameMap();
		
		try {
			writer.write("<div><h1><div id=\"box\"> </div>&nbsp; ����Ʈ�� ����</h1>");
			writer.write("<table cellpadding=\"5px\" id=\"deviceInfo\" border=\"1\" rules=\"all\" align=\"center\">");

			String model = Build.MODEL;
			String modelUpper = model.toUpperCase(Locale.ENGLISH);
			
			if(deviceName.containsKey(modelUpper)) {
				String name = deviceName.get(modelUpper);
				writer.write("<tr><th width=\"30%\">�𵨸�</th><td>"
						+ name + " (" + model + ") </td></tr>");
							
			} else {
				writer.write("<tr><th width=\"30%\">�𵨸�</th><td>"
						+ Build.MODEL + "</td></tr>");
			}
			
			writer.write("<tr><th>������</th><td>"
					+ Build.MANUFACTURER + "</td></tr>");
			if (telephony.getLine1Number() != null) {
				String phoneNum =PhoneNumberUtils.formatNumber(telephony.getLine1Number());
				String phoneSplit[] = new String[3];
				
				phoneSplit = phoneNum.split("-");
				
				String asteriskPhoneNum = phoneSplit[0] + " - **** - " + phoneSplit[2];
				
				writer.write("<tr><th>��ȭ��ȣ</th><td>"
						+ asteriskPhoneNum + "</td></tr>");
			} else {
				writer.write("<tr><th>��ȭ��ȣ</th><td>"
						+ "�������� �ʽ��ϴ�." + "</td></tr>");
			}
			writer.write("<tr><th>�ü�� ����</th><td>"
					+ "Android " + Build.VERSION.RELEASE + "</td></tr>");
			
			writer.write("</table></div>");
//			writer.write("<br><br>");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	
	/* ������ �� ��� */
	private void printSpyApp() {
		try {
			if(numOfSpyApp == 0) {
				writer.write("<div id=\"contentSpyApp\"><h2>1. ������ �� ���� ��� : ������ �� ���� </h2></div>");
			} else {
				writer.write("<div id=\"contentSpyApp\"><h2>1. ������ �� ���� ��� : " + numOfSpyApp +"�� ��ġ</h2>");
				writer.write("<table id=\"spyapp\" border=\"1\" rules=\"all\" cellpadding=\"5\" align=\"center\">");
				writer.write("<tr><th id=\"appname\">�� ��Ī</th><th id=\"packname\">��Ű����</th>" +
						"<th id=\"date\">��ġ����</th><th id=\"danger\" colspan=\"2\">����</th></tr>");

				String app_name = "";
				String pack_name = "";
				String installedDate = "";
				String overall = "";

				docSpy = docBuilder.parse(spyapp);

				Element orderSpy = docSpy.getDocumentElement();
				NodeList appNode = orderSpy.getElementsByTagName("app");

				//			numOfSpyApp = Integer.parseInt(orderSpy.getAttribute("The_Number_Of_Installed_Spy_Applications"));

				for (int i = 0; i < appNode.getLength(); i++) {
					Node appItem = appNode.item(i);
					Element appEle = (Element) appItem;

					app_name = appEle.getAttribute("name");
					pack_name = appEle.getElementsByTagName("package_name").item(0).getTextContent();	
					installedDate = appEle.getElementsByTagName("installed_date").item(0).getTextContent();
					overall = getDangerity(pack_name);

					String htmlTable = "<tr id=\"" + pack_name.trim() + "\">";
					String html = "";

					html += "<td id=\"appname\">" + app_name + "</td>"
							+ "<td id=\"packname\">" + pack_name + "</td>"
							+ "<td id=\"date\">" + installedDate + "</td>"
							+ "<td id=\"hypertext\"><a href=\"javascript:delfile(\'" + pack_name.trim() + "\')\">" +
							"<img border=\"0\" src=\"garbage5.png\" width=\"20px\" height=\"17px\" /></a></td>";



					htmlTable += html + "</tr>";
					writer.write(htmlTable);

				}
				writer.write("</table></div>");
			}

		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (SAXException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	
	/* ��� �� ���� �� ��� */
	private void printVaccine() {
		try {
			if(numOfVaccineApp == 0) {
				writer.write("<div id=\"contentVaccine\"><h2> 3. ��� �� ���� P/G ���� ��� : ��� �� ���� P/G ����</h2></div>");
			} else {
				writer.write("<div id=\"contentVaccine\"><h2> 3. ��� �� ���� P/G ���� ��� : " + numOfVaccineApp + "�� ��ġ</h2>");
				writer.write("<table id=\"vaccine\" border=\"1\" rules=\"all\" cellpadding=\"5\" align=\"center\">");
				writer.write("<tr><th id=\"appname\">�� ��Ī</th><th id=\"packname\">��Ű����</th>" +
						"<th id=\"date\">��ġ����</th><th id=\"classification\">����</th></tr>");

				String app_name = "";
				String pack_name = "";
				String installedDate = "";
				String classification = "";


				docVaccine = docBuilder.parse(vaccine);		

				Element orderVaccine = docVaccine.getDocumentElement();
				NodeList appNode = orderVaccine.getElementsByTagName("app");

				//			numOfVaccineApp = Integer.parseInt(orderVaccine.getAttribute("The_Number_Of_Installed_Vaccine_Applications"));

				for (int i = 0; i < appNode.getLength(); i++) {
					Node appItem = appNode.item(i);
					Element appEle = (Element) appItem;

					app_name = appEle.getAttribute("name");

					pack_name = appEle.getElementsByTagName("package_name").item(0)
							.getTextContent();

					installedDate = appEle.getElementsByTagName("installed_date").item(0)
							.getTextContent();

					classification = appEle.getElementsByTagName("classification").item(0)
							.getTextContent();


					String htmlTable = "<tr>";
					String html = "";

					html += "<td id=\"appname\">" + app_name + "</td>"
							+ "<td id=\"packname\">" + pack_name + "</td>"
							+ "<td id=\"date\">" + installedDate + "</td>"
							+ "<td id=\"classification\">" + classification + "</td>";


					htmlTable += html + "</tr>";
					writer.write(htmlTable);

				}
				writer.write("</table></div>");
			}
		} catch (Exception e) {
			Log.e("error", e.getMessage());
			Toast.makeText(context, "Vaccineerror", Toast.LENGTH_SHORT).show();
		}
	}

	/* ���鵵 ������ �� ��� */
	private void printDangerApp() {
		try {
			if(numOfDangerApp == 0) {
				writer.write("<div id=\"contentDangerApp\"><h2> 2. ��ŷ P/G ���� ��� : ��ŷ P/G ����</h2></div>");
			} else {
				writer.write("<div id=\"contentDangerApp\">");
				writer.write("<h2> 2. ��ŷ P/G ���� ��� : " + numOfDangerApp + "�� ����</h2>");
				writer.write("<table id=\"dangerapp\" border=\"1\" rules=\"all\" cellpadding=\"5\" align=\"center\">");
				writer.write("<tr><th id=\"appname\">�� ��Ī</th><th id=\"packname\">��Ű����</th>" +
						"<th id=\"date\">��ġ����</th><th id=\"danger\" colspan=\"2\">���赵</th></tr>");

				String permission = "";
				String malignant = "";
				String app_name = "";
				String pack_name = "";
				String overall = "";
				String installedDate = "";

				setAppSet();
				setMalignantPermMap();

				Set<String> keyMalPerm = new HashSet<String>();
				keyMalPerm = descriptionMalPerm.keySet();

				docApp = docBuilder.parse(danger);		

				Element orderApp = docApp.getDocumentElement();
				NodeList appNode = orderApp.getElementsByTagName("app");

				for (int i = 0; i < appNode.getLength(); i++) {
					permission = "";
					malignant = "";

					Node appItem = appNode.item(i);
					Element appEle = (Element) appItem;
					NodeList permItems = appEle.getElementsByTagName("permission");

					if (permItems == null)
						continue;

					app_name = appEle.getAttribute("name");
					pack_name = appEle.getElementsByTagName("package_name").item(0).getTextContent();
					overall = appEle.getElementsByTagName("overall").item(0).getTextContent();
					installedDate = appEle.getElementsByTagName("installed_date").item(0).getTextContent();

					permission = "<table class=\"perm\" align=\"center\">";

					for (int j = 0; j < permItems.getLength(); j++) {
						malignant = permItems.item(j).getAttributes().item(0).getNodeValue();

						if (malignant.equals("true")) {
							if(keyMalPerm.contains(permItems.item(j).getTextContent())) {
								String korean;
								korean = descriptionMalPerm.get(permItems.item(j).getTextContent());
								permission += "<tr class=\"malignant\" id=\"package\"><td>"
										+ korean
										+ "</td></tr>";
							}
						} 
					}

					permission += "</table>";
					String htmlTable = "<tr id=\"" + pack_name + "\">";
					String html = "";

					html += "<td id=\"appname\">"+app_name+"</td>" +
							"<td id=\"packname\"><a onclick=\'this.nextSibling.style.display=(this.nextSibling.style.display==\"none\")?\"block\":\"none\";\'>"
							+ "<div class=\"app_malignant\"><b>"
							+ pack_name
							+ "</b></div>"
							+ "</a><div style=\"display: none;\">"
							+ "<br><div>" + permission + "</div></div></td>"
							+ "<td id=\"date\">" + installedDate + "</td>"
							+ "<td id=\"score\" class=\"high\" align=\"center\"><b>"
							+ overall + "%</td><td id=\"hypertext\"><a href=\"javascript:delfile(\'" + pack_name.trim() + "\')\">" +

							"<img src=\"garbage5.png\" width=\"20px\" height=\"17px\" /></a></td>";


					htmlTable += html + "</tr>";
					writer.write(htmlTable);
				}
				writer.write("</table></div>");
			}
		} catch (Exception e) {
			Log.e("error", e.getMessage());
			Toast.makeText(context, "Apperror", Toast.LENGTH_SHORT).show();
		}
		
	}
	
	
	private void printSecuritySetting(String screenLockSetting, String nfcSetting, String bluetoothSetting,
			String wifiSetting, String gpsSetting, String unknownSourceSetting) {
		try {
			writer.write("<div id=\"contentSecurity\"><h2> 4. ����������ȣ �� ���� ���� ���� ��� </h2>");
			writer.write("<table id=\"securitySetting\" cellpadding=\"5\" border=\"1\" rules=\"all\" align=\"center\">");
			
			writer.write("<tr><th width=\"16%\" title=\"���ȭ���� ��й�ȣ or ������ �����մϴ�.\">ȭ�����</th><th width=\"16%\" title=\"��������� �����ϴ� ���� �����մϴ�.\">�������</th>" +
					"<th width=\"16%\" title=\"WiFi�� �����ϴ� ���� �����մϴ�.\">Wi-Fi</th><th width=\"16%\" title=\"GPS�� �����ϴ� ���� �����մϴ�.\">GPS</th><th width=\"16%\" title=\"NFC�� �����ϴ� ���� �����մϴ�.\">NFC</th>" +
					"<th width=\"16%\" title=\"��ó�� �� �� ���� �� ����� �����ϴ� ���� �����մϴ�.\">��ó�� �� ��<br>���� �� ���</th></tr>");
			writer.write("<tr><td>"+ screenLockSetting + "</td><td>"+ bluetoothSetting + "</td><td>"
			+ wifiSetting + "</td><td>"+  gpsSetting + "</td><td>"
					+ nfcSetting + "</td><td>"+ unknownSourceSetting + "</td></tr>");
			writer.write("</table></div>");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	private void securitySetting() {
		BluetoothAdapter bluetooth = BluetoothAdapter.getDefaultAdapter();
		if(bluetooth.isEnabled())
			bluetoothSetting = "�����";
		else {
			bluetoothSetting = "����";
			numOfSecuritySetting++;
		}	
		
		WifiManager wifi = (WifiManager)context.getSystemService(Context.WIFI_SERVICE);
		if(wifi.isWifiEnabled())
			wifiSetting = "�����";
		else {
			wifiSetting = "����";
			numOfSecuritySetting++;
		}
		
		LocationManager gps = (LocationManager)context.getSystemService(Context.LOCATION_SERVICE);
		if(gps.isProviderEnabled(LocationManager.GPS_PROVIDER))
			gpsSetting = "�����";
		else {
			gpsSetting = "����";
			numOfSecuritySetting++;
		}
		
		NfcAdapter nfc = NfcAdapter.getDefaultAdapter(context);
		if(nfc == null) {
			nfcSetting = "��� ����";
		} else {
			if(nfc.isEnabled())
				nfcSetting = "�����";
			else {
				nfcSetting = "����";
				numOfSecuritySetting++;
			}
		}
		
		try {
			if(Settings.Secure.getInt(context.getContentResolver(), Settings.Secure.INSTALL_NON_MARKET_APPS) == 1)
				unknownSourceSetting = "���";
			else {
				unknownSourceSetting = "����";
				numOfSecuritySetting++;
			}
		} catch (SettingNotFoundException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		
		
		KeyguardManager km = (KeyguardManager)context.getSystemService(Context.KEYGUARD_SERVICE);
		if(km.isKeyguardSecure()) {
			try {
				if(Settings.Secure.getInt(context.getContentResolver(), Settings.Secure.LOCK_PATTERN_ENABLED) == 0)
					screenLockSetting = "��й�ȣ";
				else
					screenLockSetting = "����";
			} catch (SettingNotFoundException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			numOfSecuritySetting++;
		}
		else
			screenLockSetting = "�̼���";	
	}
	
	
	/* HTML �ݱ� */
	private void closeHTML() {
		try {
			writer.write("</div></td><td id=\"side\"> </td></tr><tr id=\"footer\"><td id=\"side\"> </td><td id=\"main\"> </td><td id=\"side\"> </td></tr></table>" +
					"</div></body></html>");
			writer.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}


	private String getDangerity(String packName) {
		String overall = "";

		try {
			docApp = docBuilder.parse(app);

			Element orderApp = docApp.getDocumentElement();
			NodeList appNode = orderApp.getElementsByTagName("app");

			for (int i = 0; i < appNode.getLength(); i++) {
				int index = 0;

				Node appItem = appNode.item(index);
				Element appEle = (Element) appItem;
				NodeList packNode = appEle.getElementsByTagName("package_name");
				Node packItem = packNode.item(0);
				Element packEle = (Element) packItem;

				while (!packName.equals(packEle.getTextContent())) {
					appItem = appNode.item(index++);
					appEle = (Element) appItem;
					packNode = appEle.getElementsByTagName("package_name");
					packItem = packNode.item(0);
					packEle = (Element) packItem;
				}

				overall = appEle.getElementsByTagName("overall").item(0)
						.getTextContent();
			}		

		} catch (SAXException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}	
		
		return overall;
	}


//	private void setVaccineSet() {
//		
//		String pack_name = "";
//		
//		try {
//			docVaccine = docBuilder.parse(vaccine);
//		} catch (SAXException e) {
//			// TODO Auto-generated catch block
//			e.printStackTrace();
//		} catch (IOException e) {
//			// TODO Auto-generated catch block
//			e.printStackTrace();
//		}
//		
//		Element orderVaccine = docVaccine.getDocumentElement();
//		NodeList vaccineNode = orderVaccine.getElementsByTagName("app");
//		
//		
//		for(int i = 0; i < vaccineNode.getLength(); i++) {
//			Node vaccineItem = vaccineNode.item(i);
//			Element vaccineEle = (Element) vaccineItem;
//			
////			app_name = vaccineEle.getAttribute("name");
//			pack_name = vaccineEle.getElementsByTagName("package_name").item(0).getTextContent();
//
//			/* appSet�� ���ϱ�!!!!!! */
//			vaccineSet.add(pack_name);
//		}
//	}
	
	private void setAppSet() {

		String app_name = "";
		String pack_name = "";
		String overall = "";

		try {
			docApp = docBuilder.parse(app);
		} catch (SAXException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		Element order = docApp.getDocumentElement();
		NodeList appNode = order.getElementsByTagName("app");

		for (int i = 0; i < appNode.getLength(); i++) {
			// permission = "";
			// malignant = "";

			Node appItem = appNode.item(i);
			Element appEle = (Element) appItem;
			NodeList permItems = appEle.getElementsByTagName("permission");

			if (permItems == null)
				continue;

			app_name = appEle.getAttribute("name");
			pack_name = appEle.getElementsByTagName("package_name").item(0)
					.getTextContent();
			overall = appEle.getElementsByTagName("overall").item(0)
					.getTextContent();

			/* appSet�� ���ϱ�!!!!!! */
			appSet.add(new SortedApp(app_name, pack_name, overall));
		}
	}

	private void setMalignantPermMap() {
		descriptionMalPerm.put("android.permission.RECEIVE_BOOT_COMPLETED", "����Ʈ�� ����� �ڵ� ���� ����");
		descriptionMalPerm.put("android.permission.CAMERA", "���� / ������ �Կ� ����");
		descriptionMalPerm.put("android.permission.RECORD_AUDIO", "���� ���� ����");
		descriptionMalPerm.put("android.permission.READ_SMS", "���ڸ޼��� �б� ����");
		descriptionMalPerm.put("android.permission.READ_CONTACTS", "�ּҷ� �о� ���� ����");
		descriptionMalPerm.put("android.permission.READ_CALENDAR", "���� �о� ���� ����");
		descriptionMalPerm.put("android.permission.READ_PHONE_STATE", "����Ʈ�� ���� �о� ���� ����");
		descriptionMalPerm.put("android.permission.ACCESS_FINE_LOCATION", "������� ��Ȯ�� ��ġ(GPS)�� �����ϴ� ����");
		descriptionMalPerm.put("android.permission.ACCESS_NETWORK_STATE", "��Ʈ��ũ�� ���� ������ �����ϴ� ����");
		descriptionMalPerm.put("android.permission.ACCESS_SUPERUSER", "���������� �����ϴ� ����");
	}
	
	private void setDeviceNameMap() {
		try{
			InputStream device = context.getResources().openRawResource(R.raw.device_name);

			Scanner scan = new Scanner(device);
			String str;

			while (scan.hasNext()) {
				str = scan.nextLine();
				String device_name;
				String device_model;

				StringTokenizer tokened = new StringTokenizer(str, "\t");
				device_name = tokened.nextToken();
				
				do {
					device_model = tokened.nextToken();
					device_model.toUpperCase();
					deviceName.put(device_model, device_name);
				} while(tokened.hasMoreTokens());
			}
			scan.close();
			device.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	private String getDate() {
		SimpleDateFormat formatter = new SimpleDateFormat("yy.MM.dd HH:mm");

		Calendar calendar = Calendar.getInstance();
		calendar.setTimeInMillis(System.currentTimeMillis());
		String strDate = formatter.format(calendar.getTime());

		return "\'"+strDate;
	}

	private void startReport() {
		try {
			
			writer.write("<br><br><div id=\"mainTitle\">");
			writer.write("�����̾� ���� ���");
			writer.write("</div><br><br><br><br>");
//			writer.write("<img src=\"sub01.png\" id=\"sub\" />");
			writer.write("<div id=\"startReport\">");
			printCheckDate();
			printDeviceInfo();
			writer.write("</div><br>");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
	/* ��� ���� ��� */
	private void briefInfo() {
		String spyapp_bf = "";
		String vaccine_bf = "";
		String dangerapp_bf = "";
		String securitysetting_bf = "";
		
		try {
//			writer.write("<img src=\"sub02.png\" id=\"sub\" /><br><br>");
			writer.write("<div id=\"briefInfo\"><h1><div id=\"box\"> </div>&nbsp; ���� ��� (���)</h1>");
			writer.write("<table border=\"1\" cellpadding=\"5\" id=\"contentBriefInfo\" align=\"center\" rules=\"all\">");
			writer.write("<tr><th width=\"25%\">�����̾�</th><th width=\"25%\">��� �� ���Ⱦ�</th>" +
					"<th width=\"25%\">���赵 ���� ��</th><th width=\"25%\">��Ÿ ���ȼ���</th></tr>");
			
			docSpy = docBuilder.parse(spyapp);			
			Element orderSpy = docSpy.getDocumentElement();			
			numOfSpyApp = Integer.parseInt(orderSpy.getAttribute("The_Number_Of_Installed_Spy_Applications"));
			
			docApp = docBuilder.parse(danger);		
			Element orderApp = docApp.getDocumentElement();
			numOfDangerApp = Integer.parseInt(orderApp.getAttribute("The_Number_Of_Danger_Applications"));
			
			docVaccine = docBuilder.parse(vaccine);		
			Element orderVaccine = docVaccine.getDocumentElement();
			numOfVaccineApp = Integer.parseInt(orderVaccine.getAttribute("The_Number_Of_Installed_Vaccine_Applications"));
			
			securitySetting();
			
			if(numOfSpyApp == 0)
				spyapp_bf = "����";
			else
				spyapp_bf += numOfSpyApp + "��";
			
			if(numOfVaccineApp == 0)
				vaccine_bf = "����";
			else
				vaccine_bf += numOfVaccineApp + "��";
			
			if(numOfDangerApp == 0)
				dangerapp_bf = "����";
			else
				dangerapp_bf += numOfDangerApp + "��";
			
			if(numOfSecuritySetting == 6)
				securitysetting_bf = "��ȣ";
			else if(numOfSecuritySetting > 2 && numOfSecuritySetting < 6)
				securitysetting_bf = "����";
			else
				securitysetting_bf = "���";
			
			writer.write("<tr><td>"+spyapp_bf+"</td><td>"+vaccine_bf+"</td><td>"+dangerapp_bf+"</td><td>"+securitysetting_bf+"</td></tr>");
			writer.write("</table></div><br>");
			
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (SAXException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	/* �� ���� ��� */
	private void detailedInfo() {
		try {
//			writer.write("<img src=\"sub03.png\" id=\"sub\" />");
			writer.write("<div id=\"detailedInfo\">");
			writer.write("<h1><div id=\"box\"> </div>&nbsp; �оߺ� ���� ��� </h1>");
			printSpyApp();
			printDangerApp();
			printVaccine();
			printSecuritySetting(screenLockSetting, nfcSetting, bluetoothSetting, wifiSetting, gpsSetting, unknownSourceSetting);
			writer.write("</div>");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}	
	}
	
	@Override
	public void run() {
		// TODO Auto-generated method stub
		startWriteHTML();
		startReport();
		briefInfo();
		detailedInfo();
		closeHTML();
	}
}
