package cloudexchange.util;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.opendaylight.controller.cloudexchange.common.CloudExchangeException;
import org.opendaylight.controller.cloudexchange.common.CommonCode;
import org.opendaylight.controller.cloudexchange.common.CommonString;
import org.opendaylight.controller.cloudexchange.common.Util;
import org.opendaylight.ovsdb.lib.notation.Row;

import cloudexchange.service.testService;

public class testUtil implements testService {

	public void run() {
		boolean result = false;
		
		
		Util util = new Util();
		util.hashCode();
		Util.print("");
		Util.println("");
		
		try {
			result = Util.isEmpty(InetAddress.getByName(""));
		} catch (UnknownHostException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		result = Util.isEmpty("09");
		List<String> list = new ArrayList<String>();
		list.add("1");
		result = Util.isEmpty(list);

		result = Util.isEmpty(new Row());

		result = Util.isEmpty(new Object());

		result = Util.isEmpty(new ArrayList<String>());

		result = Util.isEmpty(new HashMap<String, String>());
		
		CommonCode cc = new CommonCode();
		cc.checkClass();
		CommonString cs = new CommonString();
		cs.checkClass();
		CloudExchangeException ce = new CloudExchangeException(0,"");
		ce.getCommon_code();
		ce.getMessage();
		ce.setCommon_code(1);
		ce.setMessage("1");

		System.out.println("result = " + result);
	}

}
