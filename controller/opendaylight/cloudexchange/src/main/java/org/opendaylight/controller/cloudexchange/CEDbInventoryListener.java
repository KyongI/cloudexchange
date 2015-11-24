package org.opendaylight.controller.cloudexchange;

import java.net.InetAddress;

import org.opendaylight.controller.cloudexchange.common.CloudExchangeException;
import org.opendaylight.controller.cloudexchange.common.CommonCode;
import org.opendaylight.controller.cloudexchange.common.CommonString;
import org.opendaylight.controller.cloudexchange.common.Util;
import org.opendaylight.controller.cloudexchange.log.Log;
import org.opendaylight.controller.cloudexchange.log.LogType;
import org.opendaylight.controller.cloudexchange.log.Logger;
import org.opendaylight.controller.sal.core.Node;
import org.opendaylight.ovsdb.lib.notation.Row;
import org.opendaylight.ovsdb.plugin.api.OvsdbInventoryListener;

/** 
* @ClassName: CEDbInventoryListener 
* @Description: TODO Cloud Exchange DB Inventory Listener Service
*  
*/ 
public class CEDbInventoryListener {
	///////////////////////////// OVSDBInventoryListener API ///////////////////////////// 

	private OvsdbInventoryListener ovsdbInventoryListener;
	private static final String CLASS_NAME = "CEDbInventoryListener";
	
	/**
	 * When an AD-SAL node is added by the OVSDB Inventory Service, Add an
	 * MD-SAL node
	 *
	 * @param node
	 *            The AD-SAL node
	 * @param address
	 *            The {@link java.net.InetAddress} of the Node
	 * @param port
	 *            The ephemeral port number used by this connection
	 */
	public void CE_nodeAdded(Node node, InetAddress address, int port) throws CloudExchangeException {
		String functionName = "CE_nodeAdded";
		
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
			log.setMsg(CommonString.ERR_DBLST_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_NODE_PARAMETER);
		} else if (Util.isEmpty(address)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBLST_INVALID_INETADDRESS_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_INETADDRESS_PARAMETER);
		} else if (port < 0) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBLST_INVALID_PORT_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_PORT_PARAMETER);
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
			if(ovsdbInventoryListener != null) 
				ovsdbInventoryListener.nodeAdded(node, address, port);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_OVSDBINVENTORYLISTENER_NODEADDED);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_OVSDBINVENTORYLISTENER_NODEADDED, e.getMessage());
		}
        log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
	}

	/**
	 * When an AD-SAL node is removed by the OVSDB Inventory Service, Remove the
	 * MD-SAL node
	 *
	 * @param node
	 *            The AD-SAL node
	 */
	public void CE_nodeRemoved(Node node) throws CloudExchangeException{
		String functionName = "CE_nodeRemoved";
		
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
			log.setMsg(CommonString.ERR_DBLST_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_NODE_PARAMETER);
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
			if(ovsdbInventoryListener != null) 
				ovsdbInventoryListener.nodeRemoved(node);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_OVSDBINVENTORYLISTENER_NODEREMOVED);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_OVSDBINVENTORYLISTENER_NODEREMOVED, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
	}

	// public void rowAdded(Node node, String tableName, String uuid, Row row);
	// //noop

	/**
	 * Handle OVSDB row updates When a Bridge row is updated and it contains a
	 * DPID then add a new OpenFlow node to the inventory A relationship is
	 * created between the OpenFlow and OVSDB nodes
	 *
	 * @param node
	 *            The AD-SAL node
	 * @param tableName
	 *            The name of the updated table
	 * @param uuid
	 *            The UUID of the updated row
	 * @param old
	 *            The old contents of the row
	 * @param row
	 *            The updated Row
	 */
	public void CE_rowUpdated(Node node, String tableName, String uuid, Row old, Row row) 
	throws CloudExchangeException{
		String functionName = "CE_rowUpdated";
		
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
			log.setMsg(CommonString.ERR_DBLST_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_NODE_PARAMETER);
		} else if (Util.isEmpty(tableName)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBLST_INVALID_TABLENAME_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_TABLENAME_PARAMETER);
		} else if (Util.isEmpty(uuid)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBLST_INVALID_UUID_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_UUID_PARAMETER);
		} else if (Util.isEmpty(old)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBLST_INVALID_OLD_ROW_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_OLD_ROW_PARAMETER);
		} else if (Util.isEmpty(row)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBLST_INVALID_NEW_ROW_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_NEW_ROW_PARAMETER);
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
			if(ovsdbInventoryListener != null) 
				ovsdbInventoryListener.rowUpdated(node, tableName, uuid, old, row);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_OVSDBINVENTORYLISTENER_ROWUPDATED);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_OVSDBINVENTORYLISTENER_ROWUPDATED, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
	}

	/**
	 * Handle OVSDB row removed When a Bridge row is removed, the OpenFlow Node
	 * is deleted The parent OVSDB node is updated and the OpenFlow node removed
	 * from it's managed-nodes list
	 *
	 * @param node
	 *            The AD-SAL node
	 * @param tableName
	 *            The name of modified table
	 * @param uuid
	 *            The UUID of the deleted row
	 * @param row
	 *            The deleted Row
	 */
	public void CE_rowRemoved(Node node, String tableName, String uuid, Row row, Object context) 
	throws CloudExchangeException{
		String functionName = "CE_rowRemoved";
		
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
			log.setMsg(CommonString.ERR_DBLST_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_NODE_PARAMETER);
		} else if (Util.isEmpty(tableName)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBLST_INVALID_TABLENAME_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_TABLENAME_PARAMETER);
		} else if (Util.isEmpty(uuid)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBLST_INVALID_UUID_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_UUID_PARAMETER);
		} else if (Util.isEmpty(row)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBLST_INVALID_ROW_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_ROW_PARAMETER);
		} else if (Util.isEmpty(context)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBLST_INVALID_CONTEXT_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBLST_INVALID_CONTEXT_PARAMETER);
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
			if(ovsdbInventoryListener != null) 
				ovsdbInventoryListener.rowRemoved(node, tableName, uuid, row, context);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_OVSDBINVENTORYLISTENER_ROWREMOVED);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_OVSDBINVENTORYLISTENER_ROWREMOVED, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}	
		
		Logger.end(CLASS_NAME,functionName);
	}
}
