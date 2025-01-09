package detect.spy.app;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import android.content.Context;
import android.os.Handler;

public class DetectDangerApp extends AppInfo implements Runnable {
		
	private int numberOfDanger;
	
	protected Document docApp;
	protected Document docVaccine;
	protected Document docSpy;
	
	private File app;
	private File vaccine;
	private File spy;
	
	List<DangerApp> listDanger = new ArrayList<DangerApp>();
	List<String> vaccineList = new ArrayList<String>();
	List<String> spyList = new ArrayList<String>();
	
	private class DangerApp {
		
		private String appName_danger;
		private String packName_danger;
		private Map<String, String> permission_danger;
		private String installedDate_danger;
		private String dangerScore_danger;
		private String malignant;
		
		public String getMalignant() {
			return malignant;
		}

		public void setMalignant(String malignant) {
			this.malignant = malignant;
		}

		public void setAppName_danger(String appName_danger) {
			this.appName_danger = appName_danger;
		}

		public void setPackName_danger(String packName_danger) {
			this.packName_danger = packName_danger;
		}

		public void setPermission_danger(Map<String, String> permission_danger) {
			this.permission_danger = permission_danger;
		}

		public void setInstalledDate_danger(String installedDate_danger) {
			this.installedDate_danger = installedDate_danger;
		}

		public void setDangerScore_danger(String dangerScore_danger) {
			this.dangerScore_danger = dangerScore_danger;
		}


		public String getAppName_danger() {
			return appName_danger;
		}

		public String getPackName_danger() {
			return packName_danger;
		}

		public Map<String, String> getPermission_danger() {
			return permission_danger;
		}

		public String getInstalledDate_danger() {
			return installedDate_danger;
		}

		public String getDangerScore_danger() {
			return dangerScore_danger;
		}

		private DangerApp(String appName, String packName, Map<String, String> permission, 
				String installedDate, String dangerScore) {

			this.appName_danger = appName;
			this.packName_danger = packName;
			this.permission_danger = permission;
			this.installedDate_danger = installedDate;
			this.dangerScore_danger = dangerScore;
		}
	}
	
	public DetectDangerApp(Context context, Handler handler, String flag) {
		super(context, handler, flag);
		// TODO Auto-generated constructor stub
		
		try {
			docFactory = DocumentBuilderFactory.newInstance();
			docBuilder = docFactory.newDocumentBuilder();
			doc = docBuilder.newDocument();
			rootElement = doc.createElement("printDangerApps");
			doc.appendChild(rootElement);
			
			app = new File(mSdPath + "/tmp/app.xml");
			vaccine = new File(mSdPath + "/tmp/vaccine.xml");
			spy = new File(mSdPath + "/tmp/spyapp.xml");

		} catch (ParserConfigurationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	private void parsingApp() {
		
		String app_name = "";
		String pack_name = "";
		String overall = "";
		String installedDate = "";
		String malignant = "";
		
		
		try {
			docSpy = docBuilder.parse(spy);
			Element orderSpy = docSpy.getDocumentElement();
			NodeList appNode = orderSpy.getElementsByTagName("app");
			
			for(int i = 0; i < appNode.getLength(); i++) {
				Node appItem = appNode.item(i);
				Element appEle = (Element) appItem;
				
				spyList.add(appEle.getElementsByTagName("package_name").item(0).getTextContent());
			}
			
			
			docVaccine = docBuilder.parse(vaccine);
			Element orderVaccine = docVaccine.getDocumentElement();
			appNode = orderVaccine.getElementsByTagName("app");
			
			for(int i = 0; i < appNode.getLength(); i++) {
				Node appItem = appNode.item(i);
				Element appEle = (Element) appItem;
				
				vaccineList.add(appEle.getElementsByTagName("package_name").item(0).getTextContent());
			}
			
			
			docApp = docBuilder.parse(app);
			Element orderApp = docApp.getDocumentElement();
			appNode = orderApp.getElementsByTagName("app");
			NodeList permItems;
			
			
			for(int i = 0; i < appNode.getLength(); i++) {				
				Node appItem = appNode.item(i);
				Element appEle = (Element) appItem;

				Element level = (Element) appEle.getElementsByTagName("overall").item(0);
				if(level.getAttribute("level").equals("high")) {
					if(!vaccineList.contains(appEle.getElementsByTagName("package_name").item(0).getTextContent())) {
						if(!spyList.contains(appEle.getElementsByTagName("package_name").item(0).getTextContent())) {
							Map<String, String> perm = new HashMap<String, String>();
							DangerApp danger = new DangerApp(app_name, pack_name, perm, installedDate, overall);

							app_name = appEle.getAttribute("name");
							danger.setAppName_danger(app_name);

							malignant = appEle.getAttribute("app_malignant");
							danger.setMalignant(malignant);

							pack_name = appEle.getElementsByTagName("package_name").item(0).getTextContent();
							danger.setPackName_danger(pack_name);

							installedDate = appEle.getElementsByTagName("installed_date").item(0).getTextContent();
							danger.setInstalledDate_danger(installedDate);

							permItems = appEle.getElementsByTagName("permission");
							for(int j = 0; j < permItems.getLength(); j++) {
								perm.put(permItems.item(j).getTextContent(), permItems.item(j).getAttributes().item(0).getTextContent());
							}
							danger.setPermission_danger(perm);

							overall = appEle.getElementsByTagName("overall").item(0).getTextContent();
							danger.setDangerScore_danger(overall);

							listDanger.add(danger);
						}
					}
				} else
					continue;
			}		
		} catch (SAXException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	private void makeDangerApp() {
		
		for(int i = 0; i < listDanger.size(); i++) {
			DangerApp danger = listDanger.get(i);
			if(Boolean.parseBoolean(danger.getMalignant())) {
				numberOfDanger++;
				Element app = doc.createElement("app");
				rootElement.appendChild(app);
				app.setAttribute("name", danger.getAppName_danger());

				Element pack = doc.createElement("package_name");
				pack.appendChild(doc.createTextNode(danger.getPackName_danger()));
				app.appendChild(pack);

				Element installed_date = doc.createElement("installed_date");
				installed_date.appendChild(doc.createTextNode(danger.getInstalledDate_danger()));
				app.appendChild(installed_date);


				Set<String> keySet = new HashSet<String>();
				keySet = danger.getPermission_danger().keySet();
				Iterator<String> iter = keySet.iterator();
				for(int j = 0; j < keySet.size(); j++) {

					String key = iter.next();
					if(Boolean.parseBoolean(danger.getPermission_danger().get(key))) {
						Element permission = doc.createElement("permission");
						permission.appendChild(doc.createTextNode(key));
						permission.setAttribute("malignant", danger.getPermission_danger().get(key));
						app.appendChild(permission);
					}

				}

				Element overall = doc.createElement("overall");
				overall.appendChild(doc.createTextNode(danger.getDangerScore_danger()));
				app.appendChild(overall);
			}
		}
		rootElement.setAttribute("The_Number_Of_Danger_Applications", ""+numberOfDanger);
	}
	
	@Override
	public void run() {
		// TODO Auto-generated method stub
		
		parsingApp();
		makeDangerApp();
		saveFileExternalMemory();
		mHandler.sendEmptyMessage(3);
	}

}
