package cloudexchange.service;

import org.opendaylight.controller.cloudexchange.Activator;
import org.opendaylight.controller.cloudexchange.CloudExchange;

public class testCloudExchange implements testService{

	public void run() {
		String tmp = "";
		Activator a = new Activator();
		a.init();
		a.destroy();
		a.getImplementations();
		try {
			a.configureInstance(null, null, "");
		} catch (Exception e) {
			tmp = null;
		}
		
		try {
			a.configureInstance(null, CloudExchange.class, "");
		} catch (Exception e) {
			tmp = null;
		}
		
		boolean isDebug = CloudExchange.getInstance().isDebug();
		
		System.out.println("isDebug = "+isDebug);
		
	}

}
