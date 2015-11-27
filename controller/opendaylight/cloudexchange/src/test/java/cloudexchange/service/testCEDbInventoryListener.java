package cloudexchange.service;

import org.opendaylight.controller.cloudexchange.CEDbInventoryListener;
import org.opendaylight.controller.cloudexchange.common.CloudExchangeException;

public class testCEDbInventoryListener implements testService{
	
	CEDbInventoryListener cdil = null;
	
	
	
	public testCEDbInventoryListener() {
		super();
		cdil = new CEDbInventoryListener();
	}



	public void run() {
		try {
			cdil.CE_nodeAdded(null, null, 0);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cdil.CE_nodeAdded(null, null, -1);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		
		
		try {
			cdil.CE_rowUpdated(null, "tableName", "uuid", null, null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cdil.CE_rowUpdated(null, null, "uuid", null, null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cdil.CE_rowUpdated(null, "tableName", null, null, null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cdil.CE_nodeRemoved(null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cdil.CE_rowRemoved(null, "tableName", "uuid", null, new Object());
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cdil.CE_rowRemoved(null, null, "uuid", null, new Object());
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cdil.CE_rowRemoved(null, "tableName", null, null, new Object());
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		try {
			cdil.CE_rowRemoved(null, "tableName", "uuid", null, null);
		} catch (CloudExchangeException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}
