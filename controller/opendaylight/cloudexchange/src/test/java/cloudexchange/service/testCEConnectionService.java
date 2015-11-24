package cloudexchange.service;

import org.opendaylight.controller.cloudexchange.CEConnectionService;
import org.opendaylight.controller.cloudexchange.common.CloudExchangeException;

public class testCEConnectionService implements testService{
	CEConnectionService cecs = null;
	
	public testCEConnectionService() {
		super();
		cecs = new CEConnectionService();
	}

	public void run(){
		try {
			cecs.CE_connect("identifier", null);
		} catch (CloudExchangeException e) {
			e.printStackTrace();
		}
		
		try {
			cecs.CE_getConnection(null);
		} catch (CloudExchangeException e) {
			e.printStackTrace();
		}
		
		try {
			cecs.CE_getNodes();
		} catch (CloudExchangeException e) {
			e.printStackTrace();
		}
	}
	
}
