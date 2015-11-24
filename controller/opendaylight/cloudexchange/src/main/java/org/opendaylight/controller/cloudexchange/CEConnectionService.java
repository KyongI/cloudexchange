package org.opendaylight.controller.cloudexchange;

import java.util.List;
import java.util.Map;

import org.opendaylight.controller.cloudexchange.common.CloudExchangeException;
import org.opendaylight.controller.cloudexchange.common.CommonCode;
import org.opendaylight.controller.cloudexchange.common.CommonString;
import org.opendaylight.controller.cloudexchange.common.Util;
import org.opendaylight.controller.cloudexchange.log.Log;
import org.opendaylight.controller.cloudexchange.log.LogType;
import org.opendaylight.controller.cloudexchange.log.Logger;
import org.opendaylight.controller.sal.connection.ConnectionConstants;
import org.opendaylight.controller.sal.core.Node;
import org.opendaylight.ovsdb.plugin.Connection;
import org.opendaylight.ovsdb.plugin.ConnectionService;

/** 
* @ClassName: CEConnectionService 
* @Description: TODO Cloud Exchange Connection Service
*  
*/ 
public class CEConnectionService {
	///////////////////////////// IConnectionServiceInternal API ///////////////////////////// //////////////////////////
	
	private ConnectionService connectionServiceInternal;
	private static final String CLASS_NAME = "CEConnectionService";

	/**
	 * Deprecated. Specified by: getConnection in interface
	 * OvsdbConnectionService Specified by: getConnection in interface
	 * IConnectionServiceInternal
	 */
	public Connection CE_getConnection(Node node) throws CloudExchangeException{
		Connection result = null;
		
		
		String functionName = "CE_getConnection";
		
		Log log = new Log();
		log.setClassName(CLASS_NAME);
		log.setFunctionName(functionName);
		
		Logger.start(CLASS_NAME,functionName);
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.VALIDITY_START);
		log.setMsg(CommonString.INFO_VALIDITY_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		if (Util.isEmpty(node)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_CONNSRV_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_CONNSRV_INVALID_NODE_PARAMETER);
		} 
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.VALIDITY_END);
		log.setMsg(CommonString.INFO_VALIDITY_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
	    log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_START);
		log.setMsg(CommonString.INFO_SERVICE_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}		

		try {
			if(connectionServiceInternal != null) 
				result = connectionServiceInternal.getConnection(node);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_CONNECTIONSERVICEINTERNAL_GETCONNECTION);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_CONNECTIONSERVICEINTERNAL_GETCONNECTION, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
		
		return result;
	}

	/**
	 * Deprecated. Specified by: getNodes in interface OvsdbConnectionService
	 * Specified by: getNodes in interface IConnectionServiceInternal
	 */
	public List<Node> CE_getNodes() throws CloudExchangeException{
		List<Node> result = null;
		
		String functionName = "CE_getNodes";
		
		Log log = new Log();
		log.setClassName(CLASS_NAME);
		log.setFunctionName(functionName);
		
		Logger.start(CLASS_NAME,functionName);
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_START);
		log.setMsg(CommonString.INFO_SERVICE_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		try {
			if(connectionServiceInternal != null) 
				result = connectionServiceInternal.getNodes();
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_CONNECTIONSERVICEINTERNAL_GETNODES);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_CONNECTIONSERVICEINTERNAL_GETNODES, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
		
		return result;
	}

	/**
	 * Deprecated. Specified by: connect in interface
	 * org.opendaylight.controller.sal.connection.IPluginInConnectionService
	 * Specified by: connect in interface OvsdbConnectionService Specified by:
	 * connect in interface IConnectionServiceInternal
	 */
	public Node CE_connect(String identifier, Map<ConnectionConstants, String> params) 
	throws CloudExchangeException{
		Node result = null;
		
		
		String functionName = "CE_connect";
		
		Log log = new Log();
		log.setClassName(CLASS_NAME);
		log.setFunctionName(functionName);
		
		Logger.start(CLASS_NAME,functionName);
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.VALIDITY_START);
		log.setMsg(CommonString.INFO_VALIDITY_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		if (Util.isEmpty(identifier)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_CONNSRV_INVALID_IDENTIFIER_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_CONNSRV_INVALID_IDENTIFIER_PARAMETER);
		} else if(Util.isEmpty(params)){
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_CONNSRV_INVALID_PARAMS_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_CONNSRV_INVALID_PARAMS_PARAMETER);
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.VALIDITY_END);
		log.setMsg(CommonString.INFO_VALIDITY_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
	
	    log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_START);
		log.setMsg(CommonString.INFO_SERVICE_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		
		try {
			if(connectionServiceInternal != null) 
				result = connectionServiceInternal.connect(identifier, params);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_CONNECTIONSERVICEINTERNAL_CONNECT);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_CONNECTIONSERVICEINTERNAL_CONNECT, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
		
		return result;
	}
}
