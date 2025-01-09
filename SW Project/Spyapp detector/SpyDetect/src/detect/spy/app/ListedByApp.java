package detect.spy.app;

import java.util.ArrayList;
import java.util.Collections;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.PackageManager.NameNotFoundException;
import android.os.Handler;

public class ListedByApp extends AppInfo implements Runnable {

	private PackageInfo packInfo_app;
	private String[] permissions_app;
	private String packName_app;

	public ListedByApp(Context context, Handler handler, String flag) {
		super(context, handler, flag);
		// TODO Auto-generated constructor stub

		Items = new ArrayList<String>();
		packages = new ArrayList<ApplicationInfo>();

		try {
			docFactory = DocumentBuilderFactory.newInstance();
			docBuilder = docFactory.newDocumentBuilder();
			doc = docBuilder.newDocument();
			rootElement = doc.createElement("printAllApps");
			doc.appendChild(rootElement);

		} catch (ParserConfigurationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	private void startCreateXml() {
		setAppsList();
		getMalignantPerm();

		for (String appName : Items) {
			if (appName == Items.get(0)) {
				rootElement.setAttribute(
						"The_Number_Of_Installed_Applications", appName);
				continue;
			}

			Element app = doc.createElement("app");
			rootElement.appendChild(app);
			app.setAttribute("name", appName);
			setPermissionList(appName, app);
		}
		sortedAppAgain();
	}

	private void setAppsList() {
		packages = context.getPackageManager().getInstalledApplications(
				PackageManager.GET_META_DATA);
		int num = 0;

		for (ApplicationInfo appInfo : packages) {
			
			if ((appInfo.flags & ApplicationInfo.FLAG_SYSTEM) != 0) {
				if ((appInfo.flags & ApplicationInfo.FLAG_UPDATED_SYSTEM_APP) != 0) {
					String appName = appInfo.loadLabel(
							context.getPackageManager()).toString();
					Items.add(appName);
					num++;
				}
			} else {
				String appName = appInfo.loadLabel(context.getPackageManager())
						.toString();
				Items.add(appName);
				num++;
			}
		}
		Collections.sort(Items);
		Items.remove(myLabel);
		Items.add(0, "" + --num);
	}

	private void setPermissionList(String name, Element app) {
		ArrayList<String> malPermEachAppHas = new ArrayList<String>();
		for (ApplicationInfo appInfo : packages) {
			String appName = appInfo.loadLabel(context.getPackageManager())
					.toString();
			int numMalPerm = 0;
			if (appName == name) {
				try {
					packInfo_app = context.getPackageManager()
							.getPackageInfo(appInfo.packageName,
									PackageManager.GET_PERMISSIONS);
					permissions_app = packInfo_app.requestedPermissions;
					packName_app = packInfo_app.packageName;

					Element pack_name = doc.createElement("package_name");
					pack_name.appendChild(doc.createTextNode(packName_app));
					app.appendChild(pack_name);
					
					Element installed_date = doc.createElement("installed_date");
					installed_date.appendChild(doc.createTextNode(getInstalledDate(packName_app)));
					app.appendChild(installed_date);

					if (permissions_app != null) {
						for (String perm : permissions_app) {
							Element perm_name = doc.createElement("permission");
							if (malPerm.contains(perm)) {
								perm_name.setAttribute("malignant", "true");
								++numMalPerm;
								malPermEachAppHas.add(perm);
							} else
								perm_name.setAttribute("malignant", "false");
							perm_name.appendChild(doc.createTextNode(perm));
							app.appendChild(perm_name);
						}

						if ((numMalPerm != 0) && malPermEachAppHas.contains(mustbeMalignantPerm)) {
							app.setAttribute("app_malignant", "true");
						} else {
							app.setAttribute("app_malignant", "false");
						}
						
						Element perm_num = doc.createElement("overall");
						
						/*
						NumberFormat nf = NumberFormat.getInstance();
						nf.setMaximumFractionDigits(1);
						nf.setMinimumFractionDigits(1);
						String avg = nf.format((double)numMalPerm/malPerm.size()*100);
						*/
						
						int score;
						
						if(malPermEachAppHas.contains(mustbeMalignantPerm)) {
							score = (numMalPerm-1)*11;
							score = (int) Math.ceil(score/10.0)*10;
						} else {
							score = numMalPerm*11;
							score = (int) Math.ceil(score/10.0)*10;
						}
						
						
						
						if(score >= 50) {
							perm_num.setAttribute("level", "high");
						} else if (score > 0){
							perm_num.setAttribute("level", "low");
						}
						perm_num.appendChild(doc
								.createTextNode(""+score));
						app.appendChild(perm_num);
					} else {
						Element perm_num = doc.createElement("overall");
						perm_num.appendChild(doc
								.createTextNode("0.0"));
						app.appendChild(perm_num);
					}
					break;
				} catch (NameNotFoundException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}

		}
	}

	private void sortedAppAgain() {

		NodeList appNode = rootElement.getElementsByTagName("app");
		boolean isAppFirst = false;
		Node first = null;
		
		for (int i = 0; i < appNode.getLength(); i++) {
			Node appItem = appNode.item(i);
			Element appEle = (Element) appItem;
			String appName = appEle.getAttribute("name");
			String isAppMal = appEle.getAttribute("app_malignant");
			
			if (isAppMal.equals("true")) {
				if (!isAppFirst)
					continue;
				rootElement.removeChild(appItem);
			} else {
				if (!isAppFirst) {
					isAppFirst = true;
					first = appNode.item(i);
				}
				continue;
			}
			Element app = doc.createElement("app");
			rootElement.insertBefore(app, first);
			app.setAttribute("name", appName);
			setPermissionList(appName, app);
		}
	}

	
	public void run() {
		// TODO Auto-generated method stub
		startCreateXml();
		saveFileExternalMemory();
		mHandler.sendEmptyMessage(1);
	}

}
