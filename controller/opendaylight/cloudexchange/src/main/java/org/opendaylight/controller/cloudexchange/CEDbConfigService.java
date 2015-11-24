package org.opendaylight.controller.cloudexchange;

import java.util.List;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.ExecutionException;

import org.opendaylight.controller.cloudexchange.common.CloudExchangeException;
import org.opendaylight.controller.cloudexchange.common.CommonCode;
import org.opendaylight.controller.cloudexchange.common.CommonString;
import org.opendaylight.controller.cloudexchange.common.Util;
import org.opendaylight.controller.cloudexchange.log.Log;
import org.opendaylight.controller.cloudexchange.log.LogType;
import org.opendaylight.controller.cloudexchange.log.Logger;
import org.opendaylight.controller.sal.core.Node;
import org.opendaylight.controller.sal.utils.Status;
import org.opendaylight.ovsdb.lib.notation.Row;
import org.opendaylight.ovsdb.lib.schema.GenericTableSchema;
import org.opendaylight.ovsdb.plugin.api.StatusWithUuid;
import org.opendaylight.ovsdb.plugin.impl.ConfigurationServiceImpl;

/** 
* @ClassName: CEDbConfigService 
* @Description: TODO Cloud Exchange DB Config Service
*  
*/ 
public class CEDbConfigService {
	private ConfigurationServiceImpl ovsdbConfigService;
	private static final String CLASS_NAME = "CEDbConfigService";
		
	///////////////////////////// ovsdbConfigService API ///////////////////////////// //////////////////////////
	/**
	 * This version of insertRow is a short-term replacement for the older & now
	 * deprecated method of the same name. This API assumes an Open_vSwitch
	 * database Schema.
	 *
	 * @param node
	 *            OVSDB Node
	 * @param tableName
	 *            Table on which the row is inserted
	 * @param parentUuid
	 *            UUID of the parent table to which this operation will result
	 *            in attaching/mutating.
	 * @param row
	 *            Row of table Content to be inserted
	 * @return UUID of the inserted Row
	 */
	public StatusWithUuid CE_insertRow(Node node, String tableName, String parentUuid, Row<GenericTableSchema> row)
	throws CloudExchangeException{
		StatusWithUuid statusuid = null;
		String functionName = "CE_insertRow";
		
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
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
		} else if (Util.isEmpty(tableName)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_TABLENAME_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_TABLENAME_PARAMETER);
		} else if (Util.isEmpty(parentUuid)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_PARENTUUID_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_PARENTUUID_PARAMETER);
		}else if (Util.isEmpty(row)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_ROW_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_ROW_PARAMETER);
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
			if(ovsdbConfigService != null)
				statusuid = ovsdbConfigService.insertRow(node, tableName, parentUuid, row);
		} catch (Exception e) {
			//log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_CEDBCONFIGSERVICE_CE_INSERTROW);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_CEDBCONFIGSERVICE_CE_INSERTROW, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
		
		return statusuid;
	}

	/**
	 * This version of updateRow is a short-term replacement for the older & now
	 * deprecated method of the same name. This API assumes an Open_vSwitch
	 * database Schema.
	 *
	 * @param node
	 *            OVSDB Node
	 * @param tableName
	 *            Table on which the row is Updated
	 * @param parentUuid
	 *            UUID of the parent row on which this operation might result in
	 *            mutating.
	 * @param rowUuid
	 *            UUID of the row that is being updated
	 * @param row
	 *            Row of table Content to be Updated. Include just those columns
	 *            that needs to be updated.
	 */
	public Status CE_updateRow(Node node, String tableName, String parentUuid, String rowUuid, Row row)
	throws CloudExchangeException{
		Status status = null;
		String functionName = "CE_updateRow";
		
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
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
		} else if (Util.isEmpty(tableName)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_TABLENAME_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_TABLENAME_PARAMETER);
		} else if (Util.isEmpty(parentUuid)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_PARENTUUID_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_PARENTUUID_PARAMETER);
		} else if (Util.isEmpty(rowUuid)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_ROWUUID_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_ROWUUID_PARAMETER);
		} else if (Util.isEmpty(row)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_ROW_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_ROW_PARAMETER);
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
			if(ovsdbConfigService != null)
				status = ovsdbConfigService.updateRow(node, tableName, parentUuid, rowUuid, row);
		} catch (Exception e) {
			//log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_CEDBCONFIGSERVICE_CE_UPDATEROW);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_CEDBCONFIGSERVICE_CE_UPDATEROW, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
		
		return status;
	}

	/**
	 * This version of deleteRow is a short-term replacement for the older & now
	 * deprecated method of the same name. This API assumes an Open_vSwitch
	 * database Schema.
	 *
	 * @param node
	 *            OVSDB Node
	 * @param tableName
	 *            Table on which the row is Updated
	 * @param rowUuid
	 *            UUID of the row that is being deleted
	 */
	public Status CE_deleteRow(Node node, String tableName, String rowUuid)
	throws CloudExchangeException{
		Status status = null;
		String functionName = "CE_deleteRow";
		
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
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
		} else if (Util.isEmpty(tableName)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_TABLENAME_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_TABLENAME_PARAMETER);
		} else if (Util.isEmpty(rowUuid)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_ROWUUID_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_ROWUUID_PARAMETER);
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
			if(ovsdbConfigService != null)
				status = ovsdbConfigService.deleteRow(node, tableName, rowUuid);
		} catch (Exception e) {
			//log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_CEDBCONFIGSERVICE_CE_DELETEROW);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_CEDBCONFIGSERVICE_CE_DELETEROW, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
		
		return status;
	}

	/**
	 * This version of getRow is a short-term replacement for the older & now
	 * deprecated method of the same name. This API assumes an Open_vSwitch
	 * database Schema.
	 *
	 * @param node
	 *            OVSDB Node
	 * @param tableName
	 *            Table Name
	 * @param rowUuid
	 *            UUID of the row being queried
	 * @return a row with a list of Column data that corresponds to an unique
	 *         Row-identifier called uuid in a given table.
	 */
	public Row CE_getRow(Node node, String tableName, String uuid)
	throws CloudExchangeException{
		Row row = null;
		String functionName = "CE_getRow";
		
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
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
		} else if (Util.isEmpty(tableName)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_TABLENAME_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_TABLENAME_PARAMETER);
		} else if (Util.isEmpty(uuid)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_UUID_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_UUID_PARAMETER);
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
			if(ovsdbConfigService != null)
				row = ovsdbConfigService.getRow(node, tableName, uuid);
		} catch (Exception e) {
			//log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_CEDBCONFIGSERVICE_CE_GETROW);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_CEDBCONFIGSERVICE_CE_GETROW, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
		
		return row;
	}

	/**
	 * This version of getRows is a short-term replacement for the older & now
	 * deprecated method of the same name. This API assumes an Open_vSwitch
	 * database Schema.
	 *
	 * @param node
	 *            OVSDB Node
	 * @param tableName
	 *            Table Name
	 * @return List of rows that makes the entire Table.
	 */
	public ConcurrentMap<String, Row> CE_getRows(Node node, String tableName)
	throws CloudExchangeException{
		ConcurrentMap<String, Row> concurrentMap = null;
		String functionName = "CE_getRows";
		
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
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
		} else if (Util.isEmpty(tableName)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_TABLENAME_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_TABLENAME_PARAMETER);
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
			if(ovsdbConfigService != null)
				concurrentMap = ovsdbConfigService.getRows(node, tableName);
		} catch (Exception e) {
			//log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_CEDBCONFIGSERVICE_CE_GETROWS);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_CEDBCONFIGSERVICE_CE_GETROWS, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
		
		return concurrentMap;
	}

	/**
	 * Returns all the Tables in a given Ndoe. This API assumes an Open_vSwitch
	 * database Schema.
	 *
	 * @param node
	 *            OVSDB node
	 * @return List of Table Names that make up Open_vSwitch schema.
	 */
	public List<String> CE_getTables(Node node)
	throws CloudExchangeException{
		List<String> list = null;
		String functionName = "CE_getTables";
		
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
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
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
			if(ovsdbConfigService != null)
				list = ovsdbConfigService.getTables(node);
		} catch (Exception e) {
			//log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_CEDBCONFIGSERVICE_CE_GETTABLES);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_CEDBCONFIGSERVICE_CE_GETTABLES, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
		
		return list;
	}

	/**
	 * setOFController is a convenience method used by existing applications to
	 * setup Openflow Controller on a Open_vSwitch Bridge. This API assumes an
	 * Open_vSwitch database Schema.
	 *
	 * @param node
	 *            Node
	 * @param bridgeUUID
	 *            uuid of the Bridge for which the ip-address of Openflow
	 *            Controller should be programmed.
	 * @return Boolean representing success or failure of the operation.
	 *
	 * @throws InterruptedException
	 * @throws java.util.concurrent.ExecutionException
	 */
	public Boolean CE_setOFController(Node node, String bridgeUUID)
	throws InterruptedException, ExecutionException, CloudExchangeException{
		Boolean ceBoolean = null;
		String functionName = "CE_setOFController";
		
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
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
			Logger.printLog(log);
			
			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_NODE_PARAMETER);
		} else if (Util.isEmpty(bridgeUUID)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_DBCONFIG_INVALID_BRIDGEUUID_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_DBCONFIG_INVALID_BRIDGEUUID_PARAMETER);
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
			if(ovsdbConfigService != null)
				ceBoolean = ovsdbConfigService.setOFController(node, bridgeUUID);
		} catch (InterruptedException e) {
			throw e;
		} catch (ExecutionException e) {
			throw e;
		} catch (Exception e) {
			//log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_CEDBCONFIGSERVICE_CE_SETOFCONTROLLER);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_CEDBCONFIGSERVICE_CE_SETOFCONTROLLER, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}
		
		Logger.end(CLASS_NAME,functionName);
		
		return ceBoolean;
	}
}
