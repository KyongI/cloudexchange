package cloudexchange.service;

import org.opendaylight.controller.cloudexchange.CloudExchange;

public class testCloudExchange implements testService{

	public void run() {
		boolean isDebug = CloudExchange.getInstance().isDebug();
		
		System.out.println("isDebug = "+isDebug);
		
	}

}
