package detect.spy.app;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Iterator;
import java.util.TreeSet;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import android.content.Context;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.telephony.PhoneNumberUtils;
import android.telephony.TelephonyManager;
import android.util.Log;
import android.widget.Toast;

public class ConvertXMLtoHTML implements Runnable {
	
	private static class SortedApp implements Comparable<SortedApp> {	
		private String appName;
		private String packName;
		private double appPercent;
		
		SortedApp(String appName, String packName, String strAppPercent) {
//			String token;
//			StringTokenizer tokened = new StringTokenizer(strAppPercent, "%");
//			
//			token = tokened.nextToken();
			this.appPercent = Double.parseDouble(strAppPercent);
			this.appName = appName;
			this.packName = packName;
		}
		
		public String toString() {
			return appName + " : " + appPercent;
		}
		
		public int compareTo(SortedApp sa) {
			// TODO Auto-generated method stub
			
			if(appPercent > sa.appPercent) {
				return -1;
			} else if(appPercent < sa.appPercent) {
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
	
	private TreeSet<SortedApp> sortedList = new TreeSet<SortedApp>();
	private TreeSet<SortedApp> appSet = new TreeSet<SortedApp>();
	
	protected Context context;

	private String mSdPath;
	private String appFile;

	protected DocumentBuilderFactory docFactory;
	protected DocumentBuilder docBuilder;
	protected Document docApp;
	protected Document docPerm;
	protected Element rootElement;

	private File app;

	private FileWriter fWriter;
	private BufferedWriter writer;

	private Handler mHandler;

	public ConvertXMLtoHTML(Context context, String appFile, Handler handler) {
		this.context = context;
		this.appFile = appFile;
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

		try {
			fWriter = new FileWriter(mSdPath + "/tmp/Report.html");
			writer = new BufferedWriter(fWriter);

			writer.write("<!DOCTYPE html><html>	<head><meta charset=\"utf-8\"><title>REPORT</title>"
					+ "<style> .malignant { color : blue; }	a:link { color : black; } .app_malignant { color: orange; } .perm { padding-left : 30px; } .pack { padding-left : 30px; } " +
					"#header { position : fixed; width : 100%; height : 33%; border-bottom : 2px solid #cccccc; } " +
					"#content { position : fixed; width : 49%; height : 65%; top : 35%; overflow : scroll; padding-right : 10px; border-right : 2px solid #cccccc; } " +
					"#contentApp { position : fixed; width : 49.7%; height : 65%; top : 35%; margin-left : 49%; overflow-y : scroll; padding-left : 15px; } " +
					"#malignant_permission { position : fixed; width : auto; margin-left : 50%; height : auto; color : blue; font-size : 12px; }" +
					".high { color : darkred; } .low { color : salmon; } " +
					"#deviceInfo { font-size : 16px; }" +
					"</style>"
					+ "<div id=\"header\"><h2>디바이스 정보</h2> ");

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

	void printDeviceInfo() {
		TelephonyManager telephony = (TelephonyManager) context
				.getSystemService(Context.TELEPHONY_SERVICE);

		try {
			writer.write("<table id=\"deviceInfo\">");

			writer.write("<tr><td align=\"right\">브렌드 : </td><td>"
					+ Build.BRAND + "</td></tr>");
			writer.write("<tr><td align=\"right\">제조사 : </td><td>"
					+ Build.MANUFACTURER + "</td></tr>");
			writer.write("<tr><td align=\"right\">모델명 : </td><td>"
					+ Build.MODEL + "</td></tr>");
			writer.write("<tr><td align=\"right\">OS버전 : </td><td>"
					+ "Android " + Build.VERSION.RELEASE + "</td></tr>");
			if (telephony.getLine1Number() != null)
				writer.write("<tr><td align=\"right\">전화번호 : </td><td>"
						+ PhoneNumberUtils.formatNumber(telephony
								.getLine1Number()) + "</td></tr>");
			else
				writer.write("<tr><td align=\"right\">전화번호 : </td><td>"
						+ "존재하지 않습니다." + "</td></tr>");

			writer.write("</table>");
			writer.write("<br><br></div></head>");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	void makePermissionTable() {
		try {
			writer.write("<table border=\"1\" cellpadding=\"3\" id=\"malignant_permission\">");
			
			writer.write("<tr><td>android.permission.RECEIVE_BOOT_COMPLETED</td><td> 스마트폰 실행시 자동 실행 권한 </td></tr>");
			writer.write("<tr><td>android.permission.RECORD_AUDIO</td><td> 음성 녹음 권한 </td></tr>");
			writer.write("<tr><td>android.permission.CAMERA</td><td> 사진 / 동영상 촬영 권한 </td></tr>");
			writer.write("<tr><td>android.permission.READ_SMS</td><td> 문자메세지 읽기 권한 </td></tr>");
			writer.write("<tr><td>android.permission.WRITE_SMS</td><td> 문자메세지 쓰기 권한 </td></tr>");
			writer.write("<tr><td>android.permission.SEND_SMS</td><td> 문자메세지 발송 권한 </td></tr>");
			writer.write("<tr><td>android.permission.READ_CONTACTS</td><td> 주소록 읽어 오는 권한 </td></tr>");
			writer.write("<tr><td>android.permission.READ_PHONE_STATE</td><td> 스마트폰 정보 읽어 오는 권한 </td></tr>");
			
			writer.write("</table>");

		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	
	
	
	
	
	private void printSpyApp() {
		
	}
	
	private void printVaccine() {
		
	}
	
	
	
	void convertApp() {
		try {
			writer.write("<body><div id=\"content\">");
			writer.write("<span id=\"content\"><h2 align=\"center\">앱 명칭</h2>");
			writer.write("<table border=\"1\" cellpadding=\"5\" align=\"center\">");

			String permission = "";
			String malignant = "";
			String app_name = "";
			String pack_name = "";
			String overall = "";
			String overallLevel = "";
			String app_mal = "";
			

			docApp = docBuilder.parse(app);

			Element order = docApp.getDocumentElement();
			NodeList appNode = order.getElementsByTagName("app");

			for (int i = 0; i < appNode.getLength(); i++) {
				permission = "";
				malignant = "";

				Node appItem = appNode.item(i);
				Element appEle = (Element) appItem;
				NodeList permItems = appEle.getElementsByTagName("permission");

				if (permItems == null)
					continue;

				app_name = appEle.getAttribute("name");
				app_mal = appEle.getAttribute("app_malignant");

				pack_name = appEle.getElementsByTagName("package_name").item(0)
						.getTextContent();
				overall = appEle.getElementsByTagName("overall").item(0)
						.getTextContent();
				Element overEle = (Element) appEle.getElementsByTagName("overall").item(0);
				overallLevel = overEle.getAttribute("level");

				permission = "<table class=\"pack\">";
				
				
				/* appSet에 더하기!!!!!! */
				appSet.add(new SortedApp(app_name, pack_name, overall));
				
				for (int j = 0; j < permItems.getLength(); j++) {
					malignant = permItems.item(j).getAttributes().item(0)
							.getNodeValue();

					if (malignant.equals("true")) {
						permission += "<tr class=\"malignant\" id=\"package\"><td>" + permItems.item(j).getTextContent() + "</td></tr>";
					} else {
						permission += "<tr id=\"package\"><td>" + permItems.item(j).getTextContent() + "</td></tr>";
					}

				}
				permission += "</table>";
				String htmlTable = "<tr>";
				String html = "";

				if (app_mal.equals("true")) {
					html += "<td><a onclick=\'this.nextSibling.style.display=(this.nextSibling.style.display==\"none\")?\"block\":\"none\";\'>"
							+ "<div class=\"app_malignant\"><b>"
							+ "["
							+ app_name
							+ "] ---- ["
							+ pack_name
							+ "]"
							+ "</b></div>"
							+ "</a><div style=\"display: none;\">"
							+ "<br><div>"
							+ permission
							+ "</div></div></td>";
					if(overallLevel.equals("high"))		
						html += "<td class=\"high\" align=\"center\"><b>" + overall + "%</td>";
					else if(overallLevel.equals("low"))
						html += "<td class=\"low\" align=\"center\"><b>" + overall + "%</td>";
				} else {
					html += "<td><a onclick=\'this.nextSibling.style.display=(this.nextSibling.style.display==\"none\")?\"block\":\"none\";\'>"
							+ "<div><b>"
							+ "["
							+ app_name
							+ "] ---- ["
							+ pack_name
							+ "]"
							+ "</b></div>"
							+ "</a><div style=\"display: none;\">"
							+ "<br><div>"
							+ permission
							+ "</div></div></td><td align=\"center\">"
							+ overall + "%</td>";
				}
				
				htmlTable += html + "</tr>";
				writer.write(htmlTable);
			}

			writer.write("</table></span>");

		} catch (Exception e) {
			Log.e("error", e.getMessage());
			Toast.makeText(context, "Apperror", Toast.LENGTH_SHORT).show();
		}
	}

	private void closeHTML() {
		try {
			writer.write("</div></body></html>");
			writer.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	/* 위헙도 순으로 앱 출력 */
	private void printSortedApp() {
		try {
			writer.write("<span id=\"contentApp\"><h2 align=\"center\">앱 위험도 순</h2>");
			writer.write("<table border=\"1\" cellpadding=\"5\" align=\"center\">");

			String permission = "";
			String malignant = "";
			String app_name = "";
			String pack_name = "";
			String overall = "";
			String overallLevel = "";
			String app_mal = "";
			
			Iterator<SortedApp> iter = appSet.iterator();
			
			docApp = docBuilder.parse(app);

			Element order = docApp.getDocumentElement();
			NodeList appNode = order.getElementsByTagName("app");
			
			
			for (int i = 0; i < appNode.getLength(); i++) {
				permission = "";
				malignant = "";
				int index = 0;

				Node appItem = appNode.item(0);
				Element appEle = (Element) appItem;
				
				app_name = iter.next().getAppName();
				
				while(!app_name.equals(appEle.getAttribute("name"))) {
					appItem = appNode.item(index++);
					appEle = (Element) appItem;
				}
				
				NodeList permItems = appEle.getElementsByTagName("permission");

				if (permItems == null)
					continue;
	
				app_mal = appEle.getAttribute("app_malignant");

				pack_name = appEle.getElementsByTagName("package_name").item(0)
						.getTextContent();
				overall = appEle.getElementsByTagName("overall").item(0)
						.getTextContent();
				Element overEle = (Element) appEle.getElementsByTagName("overall").item(0);
				overallLevel = overEle.getAttribute("level");

				permission = "<table class=\"pack\">";
				
				for (int j = 0; j < permItems.getLength(); j++) {
					malignant = permItems.item(j).getAttributes().item(0)
							.getNodeValue();

					if (malignant.equals("true")) {
						permission += "<tr class=\"malignant\" id=\"package\"><td>" + permItems.item(j).getTextContent() + "</td></tr>";
					} else {
						permission += "<tr id=\"package\"><td>" + permItems.item(j).getTextContent() + "</td></tr>";
					}

				}
				permission += "</table>";
				String htmlTable = "<tr>";
				String html = "";

				if (app_mal.equals("true")) {
					html += "<td><a onclick=\'this.nextSibling.style.display=(this.nextSibling.style.display==\"none\")?\"block\":\"none\";\'>"
							+ "<div class=\"app_malignant\"><b>"
							+ "["
							+ app_name
							+ "] ---- ["
							+ pack_name
							+ "]"
							+ "</b></div>"
							+ "</a><div style=\"display: none;\">"
							+ "<br><div>"
							+ permission
							+ "</div></div></td>";
					if(overallLevel.equals("high"))		
						html += "<td class=\"high\" align=\"center\"><b>" + overall + "%</td>";
					else if(overallLevel.equals("low"))
						html += "<td class=\"low\" align=\"center\"><b>" + overall + "%</td>";
				} else {
					html += "<td><a onclick=\'this.nextSibling.style.display=(this.nextSibling.style.display==\"none\")?\"block\":\"none\";\'>"
							+ "<div><b>"
							+ "["
							+ app_name
							+ "] ---- ["
							+ pack_name
							+ "]"
							+ "</b></div>"
							+ "</a><div style=\"display: none;\">"
							+ "<br><div>"
							+ permission
							+ "</div></div></td><td align=\"center\">"
							+ overall + "%</td>";
				}
				
				htmlTable += html + "</tr>";
				writer.write(htmlTable);
			}

			writer.write("</table></span>");

		} catch (Exception e) {
			Log.e("error", e.getMessage());
			Toast.makeText(context, "Apperror", Toast.LENGTH_SHORT).show();
		}
	}
	
	public void run() {
		startWriteHTML();
		printDeviceInfo();
		makePermissionTable();
		printSortedApp();
		convertApp();
		closeHTML();
	}
}
