package org.opendaylight.controller.cloudexchange.log;

import org.opendaylight.controller.cloudexchange.common.CommonCode;

/** 
* @ClassName: Log 
* @Description: TODO Log Model
*  
*/ 
public class Log {
	private int code = CommonCode.OK_SUCCESS;
	
	private LogType type = null;
	
	private String className = null;
	
	private String functionName = null;
	
	private String msg = null;
	
	public Log(){
		super();
	}
	
	public Log(int code, LogType type, String msg) {
		super();
		this.code = code;
		this.type = type;
		this.className = "";
		this.functionName = "";
		this.msg = msg;
	}

	public Log(String msg) {
		super();
		this.type = LogType.INFO;
		this.code = CommonCode.OK_SUCCESS;
		this.className = "";
		this.functionName = "";
		this.msg = msg;
	}

	public Log(String className, String functionName, String msg) {
		super();
		this.type = LogType.INFO;
		this.code = CommonCode.OK_SUCCESS;
		this.className = className;
		this.functionName = functionName;
		this.msg = msg;
	}

	public Log(LogType type, String className, String functionName, String msg) {
		super();
		this.type = type;
		this.className = className;
		this.functionName = functionName;
		this.msg = msg;
		
		if(type == LogType.INFO) code = CommonCode.OK_SUCCESS;
		else if (type == LogType.ERROR) code = CommonCode.ERR_GENERAL;
		else code = CommonCode.OK_SUCCESS;
	}

	public Log(int code, LogType type, String className, String functionName, String msg) {
		super();
		this.code = code;
		this.type = type;
		this.className = className;
		this.functionName = functionName;
		this.msg = msg;
	}

	public String getMsg() {
		return msg;
	}

	public void setMsg(String msg) {
		this.msg = msg;
	}

	public int getCode() {
		return code;
	}

	public void setCode(int code) {
		this.code = code;
	}

	public String getClassName() {
		return className;
	}

	public void setClassName(String className) {
		this.className = className;
	}

	public String getFunctionName() {
		return functionName;
	}

	public void setFunctionName(String functionName) {
		this.functionName = functionName;
	}

	public LogType getType() {
		return type;
	}

	public void setType(LogType type) {
		this.type = type;
	}
	
	
}
