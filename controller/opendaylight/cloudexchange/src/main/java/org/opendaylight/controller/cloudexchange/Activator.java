package org.opendaylight.controller.cloudexchange;
import java.util.Dictionary;
import java.util.Hashtable;

import org.apache.felix.dm.Component;
import org.opendaylight.controller.sal.core.ComponentActivatorAbstractBase;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** 
* @ClassName: Activator 
* @Description: TODO Activator
*  
*/ 
public class Activator extends ComponentActivatorAbstractBase {

	private static final Logger LOG = LoggerFactory.getLogger(CloudExchange.class);

	/**
	 * Function called when the activator starts just after some
	 * initializations are done by the
	 * ComponentActivatorAbstractBase.
	 *
	 */
	public void init() {
		//for init
	}

	/**
	 * Function called when the activator stops just before the
	 * cleanup done by ComponentActivatorAbstractBase
	 *
	 */
	public void destroy() {
		//for destory
	}

	/**
	 * Function that is used to communicate to dependency manager the
	 * list of known implementations for services inside a container
	 *
	 *
	 * @return An array containing all the CLASS objects that will be
	 * instantiated in order to get an fully working implementation
	 * Object
	 */	
        public Object[] getImplementations() {
        	LOG.trace("Getting Implementations");

                Object[] res = { CloudExchange.class };
                return res;
        }

	/**
	 * Function that is called when configuration of the dependencies
	 * is required.
	 *
	 * @param c dependency manager Component object, used for
	 * configuring the dependencies exported and imported
	 * @param imp Implementation class that is being configured,
	 * needed as long as the same routine can configure multiple
	 * implementations
	 * @param containerName The containerName being configured, this allow
	 * also optional per-container different behavior if needed, usually
	 * should not be the case though.
	 */
        public void configureInstance(Component c, Object imp, String containerName) {
        	LOG.trace("Configuring instance");

                if (imp.equals(CloudExchange.class)) {

                        // Define exported and used services for PacketHandler component.

                        Dictionary<String, Object> props = new Hashtable<String, Object>();
                        props.put("salListenerName", "cloudexchange");
                }
        }

}
