package org.opendaylight.controller.cloudexchange.common;

/** 
* @ClassName: CloudExchangeException 
* @Description: TODO Cloud Exchange Exception Class
*  
*/ 
public class CloudExchangeException extends Exception{
	
	/**
	 * CloudExchangeException
	 */
	private static final long serialVersionUID = 8608193791713153531L;
	
	
	
	private int commonCode = CommonCode.OK_SUCCESS;
	private String message = null;
	
	public CloudExchangeException(int commonCode, String message) {
		super();
		this.commonCode = commonCode;
		this.message = message;
	}

	public int getCommon_code() {
		return commonCode;
	}

	public void setCommon_code(int commonCode) {
		this.commonCode = commonCode;
	}

	public String getMessage() {
		return message;
	}

	public void setMessage(String message) {
		this.message = message;
	}
	
	
	
}
