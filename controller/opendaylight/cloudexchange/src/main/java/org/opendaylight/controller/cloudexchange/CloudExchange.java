package org.opendaylight.controller.cloudexchange;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.util.List;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.ExecutionException;
                                                 
import org.opendaylight.ovsdb.lib.table.Interface;
import org.opendaylight.controller.networkconfig.neutron.INeutronNetworkCRUD;
import org.opendaylight.controller.networkconfig.neutron.INeutronPortCRUD;
import org.opendaylight.controller.networkconfig.neutron.NeutronCRUDInterfaces;
import org.opendaylight.controller.networkconfig.neutron.NeutronPort;

import org.opendaylight.ovsdb.lib.notation.Row;
import org.opendaylight.ovsdb.lib.schema.GenericTableSchema;
import org.opendaylight.ovsdb.plugin.api.StatusWithUuid;

import org.opendaylight.controller.sal.core.Node;
import org.opendaylight.controller.sal.utils.ServiceHelper;
import org.opendaylight.controller.sal.utils.IObjectReader;
import org.opendaylight.controller.sal.utils.Status;

public class CloudExchange {


	//private INeutronPortCRUD neutronPortService = (INeutronPortCRUD)ServiceHelper.getGlobalInstance(INeutronPortCRUD.class, this);
	//private OvsdbConfigService ovsdbTable = (OvsdbConfigService)ServiceHelper.getGlobalInstance(OvsdbConfigService.class, this);
	private INeutronPortCRUD neutronPortService = NeutronCRUDInterfaces.getINeutronPortCRUD(this);
	private OvsdbConfigService ovsdbConfigService;

        public void start() {
                System.out.println("CloudExchange API service Start.");
        }

        public void stop() {
                System.out.println("CloudExchange API service Terminate");
        }

	///////////////////////////// neutronPortService API //////////////////////////
	/**
	 * Applications call this interface method to determine if a particular
	 * Port object exists
	 *
	 * @param uuid
	 *            UUID of the Port object
	 * @return boolean
	 */
	public boolean CE_portExists(String uuid) {
		return neutronPortService.portExists(uuid);
	}

	/**
	 * Applications call this interface method to return if a particular
	 * Port object exists
	 *
	 * @param uuid
	 *            UUID of the Port object
	 * @return {@link org.opendaylight.controller.networkconfig.neutron.NeutronPort.OpenStackPorts}
	 *          OpenStack Port class
	 */
	public NeutronPort CE_getPort(String uuid) {
		return neutronPortService.getPort(uuid);
	}

	/**
	 * Applications call this interface method to return all Port objects
	 *
	 * @return List of OpenStackPorts objects
	 */
	public List<NeutronPort> CE_getAllPorts() {
		return neutronPortService.getAllPorts();
	}

	/**
	 * Applications call this interface method to add a Port object to the
	 * concurrent map
	 *
	 * @param input
	 *            OpenStackPort object
	 * @return boolean on whether the object was added or not
	 */	
	public boolean CE_addPort(NeutronPort input) {
		return neutronPortService.addPort(input);
	}

	/**
	 * Applications call this interface method to remove a Port object to the
	 * concurrent map
	 *
	 * @param uuid
	 *            identifier for the Port object
	 * @return boolean on whether the object was removed or not
	 */
	public boolean CE_removePort(String uuid) {
		return neutronPortService.removePort(uuid);
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
	public boolean CE_updatePort(String uuid, NeutronPort delta) {
		return neutronPortService.updatePort(uuid, delta);
	}

	/**
	 * Applications call this interface method to see if a MAC address is in use
	 *
	 * @param macAddress
	 *            mac Address to be tested
	 * @return boolean on whether the macAddress is already associated with a
	 * port or not
	 */
	public boolean CE_macInUse(String macAddress) {
		return neutronPortService.macInUse(macAddress);
	}

	/**
	 * Applications call this interface method to retrieve the port associated with
	 * the gateway address of a subnet
	 *
	 * @param subnetUUID
	 *            identifier of the subnet
	 * @return OpenStackPorts object if the port exists and null if it does not
	 */
	public NeutronPort CE_getGatewayPort(String subnetUUID) {
		return neutronPortService.getGatewayPort(subnetUUID);
	}

	
	///////////////////////////// ovsdbConfigService API //////////////////////////
	/**
	 * This version of insertRow is a short-term replacement for the older & now deprecated method of the same name.
	 * This API assumes an Open_vSwitch database Schema.
	 *
	 * @param node OVSDB Node
	 * @param tableName Table on which the row is inserted
	 * @param parentUuid UUID of the parent table to which this operation will result in attaching/mutating.
	 * @param row Row of table Content to be inserted
	 * @return UUID of the inserted Row
	 */
	public StatusWithUuid CE_insertRow(Node node, String tableName, String parentUuid, Row<GenericTableSchema> row) {
		return ovsdbConfigService.insertRow( node, tableName, parentUuid, row); 
	}

	/**
	 * This version of updateRow is a short-term replacement for the older & now deprecated method of the same name.
	 * This API assumes an Open_vSwitch database Schema.
	 *
	 * @param node OVSDB Node
	 * @param tableName Table on which the row is Updated
	 * @param parentUuid UUID of the parent row on which this operation might result in mutating.
	 * @param rowUuid UUID of the row that is being updated
	 * @param row Row of table Content to be Updated. Include just those columns that needs to be updated.
	 */
	public Status CE_updateRow(Node node, String tableName, String parentUuid, String rowUuid, Row row) {
		return ovsdbConfigService.updateRow( node, tableName, parentUuid, rowUuid, row);
	}

	/**
	 * This version of deleteRow is a short-term replacement for the older & now deprecated method of the same name.
	 * This API assumes an Open_vSwitch database Schema.
	 *
	 * @param node OVSDB Node
	 * @param tableName Table on which the row is Updated
	 * @param rowUuid UUID of the row that is being deleted
	 */

	public Status CE_deleteRow(Node node, String tableName, String rowUUID) {
		return ovsdbConfigService.deleteRow( node, tableName, rowUUID);
	}

	/**
	 * This version of getRow is a short-term replacement for the older & now deprecated method of the same name.
	 * This API assumes an Open_vSwitch database Schema.
	 *
	 * @param node OVSDB Node
	 * @param tableName Table Name
	 * @param rowUuid UUID of the row being queried
	 * @return a row with a list of Column data that corresponds to an unique Row-identifier called uuid in a given table.
	 */

	public Row CE_getRow(Node node, String tableName, String uuid) {
		return ovsdbConfigService.getRow( node, tableName, uuid);
	}

	/**
	 * This version of getRows is a short-term replacement for the older & now deprecated method of the same name.
	 * This API assumes an Open_vSwitch database Schema.
	 *
	 * @param node OVSDB Node
	 * @param tableName Table Name
	 * @return List of rows that makes the entire Table.
	 */

	public ConcurrentMap<String, Row> CE_getRows(Node node, String tableName) {
		return ovsdbConfigService.getRows( node, tableName);
	}

	/**
	 * Returns all the Tables in a given Ndoe.
	 * This API assumes an Open_vSwitch database Schema.
	 *
	 * @param node OVSDB node
	 * @return List of Table Names that make up Open_vSwitch schema.
	 */
	public List<String> CE_getTables(Node node) {
		return ovsdbConfigService.getTables( node);
	}

	/**
	 * setOFController is a convenience method used by existing applications to setup Openflow Controller on
	 * a Open_vSwitch Bridge.
	 * This API assumes an Open_vSwitch database Schema.
	 *
	 * @param node Node
	 * @param bridgeUUID uuid of the Bridge for which the ip-address of Openflow Controller should be programmed.
	 * @return Boolean representing success or failure of the operation.
	 *
	 * @throws InterruptedException
	 * @throws java.util.concurrent.ExecutionException
	 */
	public Boolean CE_setOFController(Node node, String bridgeUUID) throws InterruptedException, ExecutionException {
		return ovsdbConfigService.setOFController( node, bridgeUUID);
	}

	
	
}



