package org.opendaylight.controller.cloudexchange;

import java.util.List;

import org.opendaylight.controller.cloudexchange.common.CloudExchangeException;
import org.opendaylight.controller.cloudexchange.common.CommonCode;
import org.opendaylight.controller.cloudexchange.common.CommonString;
import org.opendaylight.controller.cloudexchange.common.Util;
import org.opendaylight.controller.cloudexchange.log.Log;
import org.opendaylight.controller.cloudexchange.log.LogType;
import org.opendaylight.controller.cloudexchange.log.Logger;
import org.opendaylight.controller.networkconfig.neutron.INeutronPortCRUD;
import org.opendaylight.controller.networkconfig.neutron.NeutronCRUDInterfaces;
import org.opendaylight.controller.networkconfig.neutron.NeutronPort;

/** 
* @ClassName: CEPortService 
* @Description: TODO Cloud Exchange Port Service
*  
*/ 
public class CEPortService {
	///////////////////////////// neutronPortService API
	///////////////////////////// /////////////////////////////
	///////////////////////////// //////////////////////////

	private INeutronPortCRUD neutronPortService = NeutronCRUDInterfaces.getINeutronPortCRUD(this);
	private static final String CLASS_NAME = "CEPortService";

	/**
	 * Applications call this interface method to determine if a particular Port
	 * object exists
	 *
	 * @param uuid
	 *            UUID of the Port object
	 * @return boolean
	 */
	public boolean CE_portExists(String uuid) throws CloudExchangeException {
		boolean result = false;

		String functionName = "CE_portExists";

		Log log = new Log();
		log.setClassName(CLASS_NAME);
		log.setFunctionName(functionName);

		Logger.start(CLASS_NAME, functionName);
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.VALIDITY_START);
		log.setMsg(CommonString.INFO_VALIDITY_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		if (Util.isEmpty(uuid)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_PORTSRV_INVALID_UUID_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_PORTSRV_INVALID_UUID_PARAMETER);
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
			result = neutronPortService.portExists(uuid);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_NEUTRONPORTSERVICE_PORTEXISTS);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_NEUTRONPORTSERVICE_PORTEXISTS, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		Logger.end(CLASS_NAME, functionName);

		return result;
	}

	/**
	 * Applications call this interface method to return if a particular Port
	 * object exists
	 *
	 * @param uuid
	 *            UUID of the Port object
	 * @return {@link org.opendaylight.controller.networkconfig.neutron.NeutronPort.OpenStackPorts}
	 *         OpenStack Port class
	 */
	public NeutronPort CE_getPort(String uuid) throws CloudExchangeException {
		NeutronPort result = null;

		String functionName = "CE_getPort";

		Log log = new Log();
		log.setClassName(CLASS_NAME);
		log.setFunctionName(functionName);

		Logger.start(CLASS_NAME, functionName);
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.VALIDITY_START);
		log.setMsg(CommonString.INFO_VALIDITY_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		if (Util.isEmpty(uuid)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_PORTSRV_INVALID_UUID_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_PORTSRV_INVALID_UUID_PARAMETER);
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
			result = neutronPortService.getPort(uuid);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_NEUTRONPORTSERVICE_PORTEXISTS);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_NEUTRONPORTSERVICE_PORTEXISTS, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		Logger.end(CLASS_NAME, functionName);

		return result;
	}

	/**
	 * Applications call this interface method to return all Port objects
	 *
	 * @return List of OpenStackPorts objects
	 */
	public List<NeutronPort> CE_getAllPorts() throws CloudExchangeException {
		List<NeutronPort> result = null;

		String functionName = "CE_getAllPorts";

		Log log = new Log();
		log.setClassName(CLASS_NAME);
		log.setFunctionName(functionName);

		Logger.start(CLASS_NAME, functionName);
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_START);
		log.setMsg(CommonString.INFO_SERVICE_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		try {
			result = neutronPortService.getAllPorts();
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_NEUTRONPORTSERVICE_GETALLPORTS);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_NEUTRONPORTSERVICE_GETALLPORTS, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		Logger.end(CLASS_NAME, functionName);

		return result;
	}

	/**
	 * Applications call this interface method to add a Port object to the
	 * concurrent map
	 *
	 * @param input
	 *            OpenStackPort object
	 * @return boolean on whether the object was added or not
	 */
	public boolean CE_addPort(NeutronPort input) throws CloudExchangeException {
		boolean result = false;

		String functionName = "CE_addPort";

		Log log = new Log();
		log.setClassName(CLASS_NAME);
		log.setFunctionName(functionName);

		Logger.start(CLASS_NAME, functionName);
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.VALIDITY_START);
		log.setMsg(CommonString.INFO_VALIDITY_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		if (Util.isEmpty(input)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_PORTSRV_INVALID_NEUTRONPORT_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_PORTSRV_INVALID_NEUTRONPORT_PARAMETER);
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
			result = neutronPortService.addPort(input);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_NEUTRONPORTSERVICE_ADDPORT);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_NEUTRONPORTSERVICE_ADDPORT, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		Logger.end(CLASS_NAME, functionName);

		return result;
	}

	/**
	 * Applications call this interface method to remove a Port object to the
	 * concurrent map
	 *
	 * @param uuid
	 *            identifier for the Port object
	 * @return boolean on whether the object was removed or not
	 */
	public boolean CE_removePort(String uuid) throws CloudExchangeException {
		boolean result = false;

		String functionName = "CE_removePort";

		Log log = new Log();
		log.setClassName(CLASS_NAME);
		log.setFunctionName(functionName);

		Logger.start(CLASS_NAME, functionName);
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.VALIDITY_START);
		log.setMsg(CommonString.INFO_VALIDITY_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		if (Util.isEmpty(uuid)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_PORTSRV_INVALID_NODE_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_PORTSRV_INVALID_NODE_PARAMETER);
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
			result = neutronPortService.removePort(uuid);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_NEUTRONPORTSERVICE_REMOVEPORT);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_NEUTRONPORTSERVICE_REMOVEPORT, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		Logger.end(CLASS_NAME, functionName);

		return result;
	}

	/**
	 * Applications call this interface method to edit a Port object
	 *
	 * @param uuid
	 *            identifier of the Port object
	 * @param delta
	 *            OpenStackPort object containing changes to apply
	 * @return boolean on whether the object was updated or not
	 */
	public boolean CE_updatePort(String uuid, NeutronPort delta) throws CloudExchangeException {
		boolean result = false;

		String functionName = "CE_updatePort";

		Log log = new Log();
		log.setClassName(CLASS_NAME);
		log.setFunctionName(functionName);

		Logger.start(CLASS_NAME, functionName);
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.VALIDITY_START);
		log.setMsg(CommonString.INFO_VALIDITY_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		if (Util.isEmpty(uuid)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_PORTSRV_INVALID_NODE_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_PORTSRV_INVALID_NODE_PARAMETER);
		} else if (Util.isEmpty(delta)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_PORTSRV_INVALID_NEUTRONPORT_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_PORTSRV_INVALID_NEUTRONPORT_PARAMETER);
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
			result = neutronPortService.updatePort(uuid, delta);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_NEUTRONPORTSERVICE_UPDATEPORT);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_NEUTRONPORTSERVICE_UPDATEPORT, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		Logger.end(CLASS_NAME, functionName);

		return result;
	}

	/**
	 * Applications call this interface method to see if a MAC address is in use
	 *
	 * @param macAddress
	 *            mac Address to be tested
	 * @return boolean on whether the macAddress is already associated with a
	 *         port or not
	 */
	public boolean CE_macInUse(String macAddress) throws CloudExchangeException {
		boolean result = false;

		String functionName = "CE_macInUse";

		Log log = new Log();
		log.setClassName(CLASS_NAME);
		log.setFunctionName(functionName);

		Logger.start(CLASS_NAME, functionName);
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.VALIDITY_START);
		log.setMsg(CommonString.INFO_VALIDITY_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		if (Util.isEmpty(macAddress)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_PORTSRV_INVALID_MACADDRESS_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_PORTSRV_INVALID_MACADDRESS_PARAMETER);
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
			result = neutronPortService.macInUse(macAddress);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_NEUTRONPORTSERVICE_MACINUSE);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_NEUTRONPORTSERVICE_MACINUSE, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		Logger.end(CLASS_NAME, functionName);

		return result;
	}

	/**
	 * Applications call this interface method to retrieve the port associated
	 * with the gateway address of a subnet
	 *
	 * @param subnetUUID
	 *            identifier of the subnet
	 * @return OpenStackPorts object if the port exists and null if it does not
	 */
	public NeutronPort CE_getGatewayPort(String subnetUUID) throws CloudExchangeException {
		NeutronPort result = null;

		String functionName = "CE_getGatewayPort";

		Log log = new Log();
		log.setClassName(CLASS_NAME);
		log.setFunctionName(functionName);

		Logger.start(CLASS_NAME, functionName);
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.VALIDITY_START);
		log.setMsg(CommonString.INFO_VALIDITY_START);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		if (Util.isEmpty(subnetUUID)) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_INVLIDE_PARAMETER);
			log.setMsg(CommonString.ERR_PORTSRV_INVALID_SUBNETUUID_PARAMETER);
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_INVLIDE_PARAMETER,
					CommonString.ERR_PORTSRV_INVALID_SUBNETUUID_PARAMETER);
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
			result = neutronPortService.getGatewayPort(subnetUUID);
		} catch (Exception e) {
			// log
			log.setType(LogType.ERROR);
			log.setCode(CommonCode.ERR_NEUTRONPORTSERVICE_GETGATEWAYPORT);
			log.setMsg(e.getMessage());
			Logger.printLog(log);

			throw new CloudExchangeException(CommonCode.ERR_NEUTRONPORTSERVICE_GETGATEWAYPORT, e.getMessage());
		}
		
		log.setType(LogType.INFO);
		log.setCode(CommonCode.SERVICE_END);
		log.setMsg(CommonString.INFO_SERVICE_END);
		if(CloudExchange.getInstance().isDebug()){
			Logger.printLog(log);
		}

		Logger.end(CLASS_NAME, functionName);

		return result;
	}
}
