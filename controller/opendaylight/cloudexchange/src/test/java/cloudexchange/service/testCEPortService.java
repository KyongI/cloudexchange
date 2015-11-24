package cloudexchange.service;

import org.opendaylight.controller.cloudexchange.CEPortService;
import org.opendaylight.controller.cloudexchange.common.CloudExchangeException;

public class testCEPortService implements testService{
	
	CEPortService cps = null;
	
	
	
	public testCEPortService() {
		super();
		
		cps = new CEPortService();
	}



	public void run() {
		try {
			cps.CE_addPort(null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cps.CE_getAllPorts();
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cps.CE_getGatewayPort("subnetUUID");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cps.CE_getPort("uuid");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cps.CE_macInUse("macAddress");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cps.CE_portExists("uuid");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cps.CE_removePort("uuid");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cps.CE_updatePort("uuid", null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}
