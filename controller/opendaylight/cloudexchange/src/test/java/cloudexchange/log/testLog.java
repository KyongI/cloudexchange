package cloudexchange.log;

import org.opendaylight.controller.cloudexchange.log.Log;
import org.opendaylight.controller.cloudexchange.log.LogType;
import org.opendaylight.controller.cloudexchange.log.Logger;

import cloudexchange.service.testService;

public class testLog implements testService{

	public void run() {
		Logger l = new Logger();
		l.toString();
		
		Log log = new Log();
		log.setClassName("testLog");
		log.setFunctionName("run");
		log.setCode(0);
		log.setType(LogType.INFO);
		log.setMsg("testLog running");
		
		log = new Log(0,LogType.ERROR,"");
		log = new Log("");
		log = new Log("","","");
		log = new Log(LogType.ERROR,"","","");
		Logger.printLog(log);
		log = new Log(LogType.INFO,"","","");
		Logger.printLog(log);
		log = new Log(LogType.WARNING,"","","");
		Logger.printLog(log);
		log = new Log(0,LogType.ERROR,"","","");
		
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
