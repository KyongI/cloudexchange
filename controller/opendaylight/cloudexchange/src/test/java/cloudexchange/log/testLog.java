package cloudexchange.log;

import org.opendaylight.controller.cloudexchange.log.Log;
import org.opendaylight.controller.cloudexchange.log.LogType;
import org.opendaylight.controller.cloudexchange.log.Logger;

import cloudexchange.service.testService;

public class testLog implements testService{

	public void run() {
		Log log = new Log();
		log.setClassName("testLog");
		log.setFunctionName("run");
		log.setCode(0);
		log.setType(LogType.INFO);
		log.setMsg("testLog running");
		
		Logger.start("testLog");
		Logger.end("testLog");
		
		Logger.start("testLog","run");
		Logger.end("testLog","run");
		
		Logger.printLog(log);
		
		Logger.printInfoLog(log);
		Logger.printWarningLog(log);
		Logger.printErrorLog(log);
		
		Logger.log(log);
	}
	
}
