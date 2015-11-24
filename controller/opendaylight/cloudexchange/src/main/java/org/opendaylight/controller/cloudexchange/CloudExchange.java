package org.opendaylight.controller.cloudexchange;

/** 
* @ClassName: CloudExchange 
* @Description: TODO Cloud Exchange 
*  
*/ 
public class CloudExchange {
	public static CloudExchange instance = null;
	private final static boolean ISDEBUG = true;
	
	public static CloudExchange getInstance(){
		if(instance == null){
			instance = new CloudExchange();
		}
		
		return instance;
	}
	
	/** 
	* @Title: isDebug 
	* @Description: TODO Debug Mode Check
	* @param @return
	* @return boolean
	* @throws 
	*/ 
	public boolean isDebug(){
		return ISDEBUG;
	}
	
}
