package cloudexchange.service;

import java.util.concurrent.ExecutionException;

import org.opendaylight.controller.cloudexchange.CEDbConfigService;
import org.opendaylight.controller.cloudexchange.common.CloudExchangeException;

public class testCEDbConfigService implements testService{
	
	CEDbConfigService cdcs = null;
	
	
	
	public testCEDbConfigService() {
		super();
		cdcs = new CEDbConfigService();
	}



	public void run() {
		try {
			cdcs.CE_insertRow(null, "tableName", "parentUuid", null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cdcs.CE_getTables(null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cdcs.CE_getRows(null, "tableName");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cdcs.CE_getRow(null, "tableName", "uuid");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		try {
			cdcs.CE_updateRow(null, "tableName", "parentUuid", "rowUuid", null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		try {
			cdcs.CE_deleteRow(null, "tableName", "rowUuid");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		try {
			cdcs.CE_setOFController(null, "bridgeUUID");
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (ExecutionException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}

}
