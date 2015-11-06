package org.opendaylight.controller.cloudexchange;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.ObjectInputStream;
                                                 
import org.opendaylight.ovsdb.lib.table.Interface;
import org.opendaylight.controller.networkconfig.neutron.INeutronNetworkCRUD;
import org.opendaylight.controller.networkconfig.neutron.INeutronPortCRUD;
import org.opendaylight.controller.networkconfig.neutron.NeutronCRUDInterfaces;
import org.opendaylight.controller.networkconfig.neutron.NeutronPort;
import org.opendaylight.controller.sal.utils.ServiceHelper;
import org.opendaylight.controller.sal.utils.IObjectReader;
import org.opendaylight.controller.sal.utils.Status;

public class CloudExchange {


	//private INeutronPortCRUD neutronPortService = (INeutronPortCRUD)ServiceHelper.getGlobalInstance(INeutronPortCRUD.class, this);
	private INeutronPortCRUD portInterface = NeutronCRUDInterfaces.getINeutronPortCRUD(this);

        public void start() {
                System.out.println("CloudExchange API service Start.");
        }

        public void stop() {
                System.out.println("CloudExchange API service Terminate");
        }

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

	
	/*
	public Status CE_saveConfiguration() {
		return neutronPortService.saveConfiguration();
	}

	public Object CE_readObject(ObjectInputStream ois) throws FileNotFoundException, IOException, ClassNotFoundException {
		return neutronPortService.readObject(ois);
	}
	*/
	
}



