package cloudexchange.util;

import java.util.ArrayList;
import java.util.HashMap;

import org.opendaylight.controller.cloudexchange.common.Util;
import org.opendaylight.ovsdb.lib.notation.Row;

import cloudexchange.service.testService;

public class testUtil implements testService{

	public void run() {
		boolean result = false;
		
		result = Util.isEmpty("09");
		
		result = Util.isEmpty(new Row());
		
		result = Util.isEmpty(new Object());
		
		result = Util.isEmpty(new ArrayList<String>());
		
		result = Util.isEmpty(new HashMap<String, String>());
		
		System.out.println("result = "+result);
	}
	
}
