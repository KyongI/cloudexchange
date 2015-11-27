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
		String tmp = "";
		try {
			cdcs.CE_insertRow(null, "tableName", "parentUuid", null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_insertRow(null, null, "parentUuid", null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_insertRow(null, "tableName", null, null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_insertRow(null, "tableName", "1", null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		
		
		
		try {
			cdcs.CE_getTables(null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		
		
		
		try {
			cdcs.CE_getRows(null, null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_getRows(null, "1");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		
		
		
		try {
			cdcs.CE_getRow(null, null, null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_getRow(null, "1", null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_getRow(null, null, "1");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		
		
		try {
			cdcs.CE_updateRow(null, "tableName", "parentUuid", "rowUuid", null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_updateRow(null, null, "parentUuid", "rowUuid", null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_updateRow(null, "tableName", null, "rowUuid", null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_updateRow(null,"tableName", "tableName", null, null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		
		try {
			cdcs.CE_deleteRow(null, "1", "1");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_deleteRow(null, null, "1");
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_deleteRow(null, "1", null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		
		
		
		
		try {
			cdcs.CE_setOFController(null, null);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
		try {
			cdcs.CE_setOFController(null, "1");
		} catch (Exception e) {
			// TODO Auto-generated catch block
			tmp = null;
		}
		
	}

}
