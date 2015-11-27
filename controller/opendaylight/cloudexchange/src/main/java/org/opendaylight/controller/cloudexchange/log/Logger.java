package org.opendaylight.controller.cloudexchange.log;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

import org.opendaylight.controller.cloudexchange.CloudExchange;
import org.opendaylight.controller.cloudexchange.common.Util;

/** 
* @ClassName: Logger 
* @Description: TODO Print Log
*  
*/ 
public class Logger {
	/** 
	* @Title: start 
	* @Description: TODO print start log
	* @param @param className
	* @return void
	* @throws 
	*/ 
	public static void start(String className){
		if(!CloudExchange.getInstance().isDebug()) return;
		
		Calendar calendar = Calendar.getInstance();
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMddHHmmss",Locale.ENGLISH);
		
		String time = dateFormat.format(calendar.getTime());
		
		Util.print("["+time+"]");
		if(!Util.isEmpty(className)) 
			Util.print(">>>>>> "+className+" >>>>>>");
		Util.print("\n");
	}
	
	/** 
	* @Title: end 
	* @Description: TODO print end log
	* @param @param className
	* @return void
	* @throws 
	*/ 
	public static void end(String className){
		if(!CloudExchange.getInstance().isDebug()) return;
		
		Calendar calendar = Calendar.getInstance();
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMddHHmmss",Locale.ENGLISH);
		
		String time = dateFormat.format(calendar.getTime());
		
		Util.print("["+time+"]");
		if(!Util.isEmpty(className)) 
			Util.print("<<<<<< "+className+" <<<<<<");
		Util.print("\n");
	}
	
	/** 
	* @Title: start 
	* @Description: TODO print start log
	* @param @param className
	* @param @param functionName
	* @return void
	* @throws 
	*/ 
	public static void start(String className, String functionName){
		if(!CloudExchange.getInstance().isDebug()) return;
		
		Calendar calendar = Calendar.getInstance();
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMddHHmmss",Locale.ENGLISH);
		
		String time = dateFormat.format(calendar.getTime());
		
		Util.print("["+time+"]");
		if(!Util.isEmpty(className) && !Util.isEmpty(functionName)) 
			Util.print("["+className+"] >>>>>> "+functionName+" >>>>>> ");
		Util.print("\n");
	}
	
	/** 
	* @Title: end 
	* @Description: TODO print end log
	* @param @param className
	* @param @param functionName
	* @return void
	* @throws 
	*/ 
	public static void end(String className, String functionName){
		if(!CloudExchange.getInstance().isDebug()) return;
		
		Calendar calendar = Calendar.getInstance();
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMddHHmmss",Locale.ENGLISH);
		
		String time = dateFormat.format(calendar.getTime());
		
		Util.print("["+time+"]");
		if(!Util.isEmpty(className) && !Util.isEmpty(functionName)) 
			Util.print("["+className+"] <<<<<< "+functionName+" <<<<<< ");
		Util.print("\n");
	}
	
	/** 
	* @Title: printLog 
	* @Description: TODO print log
	* @param @param log
	* @return void
	* @throws 
	*/ 
	public static void printLog(Log log){
		switch(log.getType()){
		case INFO:
			printInfoLog(log);
			break;
		case ERROR:
			printErrorLog(log);
			break;
		case WARNING:
			printWarningLog(log);
			break;
		default:
			break;
		}
	}
	
	/** 
	* @Title: printInfoLog 
	* @Description: TODO print info log
	* @param @param log
	* @return void
	* @throws 
	*/ 
	public static void printInfoLog(Log log){
		Logger.log(log);
	}
	
	/** 
	* @Title: printWarningLog 
	* @Description: TODO print warning log
	* @param @param log
	* @return void
	* @throws 
	*/ 
	public static void printWarningLog(Log log){
		Logger.log(log);
	}
	
	/** 
	* @Title: printErrorLog 
	* @Description: TODO print error log
	* @param @param log
	* @return void
	* @throws 
	*/ 
	public static void printErrorLog(Log log){
		Logger.log(log);
	}
	
	/** 
	* @Title: log 
	* @Description: TODO print log
	* @param @param log
	* @return void
	* @throws 
	*/ 
	public static void log(Log log){
		Calendar calendar = Calendar.getInstance();
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMddHHmmss",Locale.ENGLISH);
		
		String time = dateFormat.format(calendar.getTime());
		int code = log.getCode();
		String msg = log.getMsg();
		String className = log.getClassName();
		String functionName = log.getFunctionName();
		LogType type = log.getType();
		
		Util.print("["+time+"]");
		Util.print("["+type+"]");
		if(!Util.isEmpty(className) && !Util.isEmpty(functionName)) 
			Util.print("["+className+":"+functionName+"]");
		Util.print(" ("+code+")");
		Util.print(msg);
		Util.print("\n");
	}
}
