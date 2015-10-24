
##### Issue 151024 : ODL Controller실행시 로그 메세지 
- 포트 충돌이 없는 경우 Controller log 
```
ubuntu@ubuntu:~/controller/opendaylight/distribution/opendaylight/target/distribution.opendaylight-osgipackage/opendaylight$ ./run.sh 
JVM maximum memory was set to -Xmx1G.
osgi> 2015-10-22 10:10:55.790 KST [Start Level Event Dispatcher] INFO  o.o.c.c.s.internal.ClusterManager  - I'm a GossipRouter will listen on port 12001
2015-10-22 10:10:55.844 KST [Start Level Event Dispatcher] INFO  o.o.c.c.s.internal.ClusterManager  - Started GossipRouter
2015-10-22 10:10:55.845 KST [Start Level Event Dispatcher] INFO  o.o.c.c.s.internal.ClusterManager  - Starting the ClusterManager
GossipRouter started at Thu Oct 22 10:10:55 KST 2015
Listening on port 12001 bound on address 0.0.0.0/0.0.0.0
Backlog is 1000, linger timeout is 2000, and read timeout is 0
2015-10-22 10:11:00.200 KST [Start Level Event Dispatcher] INFO  o.o.c.c.i.ConfigurationService  - ConfigurationService Manager init
2015-10-22 10:11:00.607 KST [Start Level Event Dispatcher] WARN  o.o.c.u.internal.UserManager  - Network Administrator password is set to factory default. Please change the password as soon as possible.
2015-10-22 10:11:01.059 KST [ControllerI/O Thread] INFO  o.o.c.p.o.core.internal.ControllerIO  - Controller is now listening on any:6633
2015-10-22 10:11:02 KST [org.apache.catalina.mbeans.GlobalResourcesLifecycleListener] SEVERE org.apache.catalina.mbeans.GlobalResourcesLifecycleListener createMBeans No global naming context defined for server
2015-10-22 10:11:03.106 KST [ControllerI/O Thread] INFO  o.o.c.p.o.core.internal.Controller  - Switch:121.78.77.166:58508 is connected to the Controller
2015-10-22 10:11:03.194 KST [ControllerI/O Thread] INFO  o.o.c.p.o.core.internal.Controller  - Switch:121.78.77.164:41719 is connected to the Controller
2015-10-22 10:11:07.808 KST [config-pusher] INFO  o.o.y.y.d.i.s.tree.InMemoryDataTree  - Attempting to install schema contexts
2015-10-22 10:11:07.834 KST [config-pusher] INFO  o.o.c.m.s.c.u.j.ThreadExecutorStatsMXBeanImpl  - Executor com.google.common.util.concurrent.MoreExecutors$SameThreadExecutorService@7579e00d is not supported
2015-10-22 10:11:07.835 KST [config-pusher] INFO  o.o.y.y.d.i.s.tree.InMemoryDataTree  - Attempting to install schema contexts
2015-10-22 10:11:07.836 KST [config-pusher] INFO  o.o.c.m.s.c.u.j.ThreadExecutorStatsMXBeanImpl  - Executor com.google.common.util.concurrent.MoreExecutors$SameThreadExecutorService@6108ba17 is not supported
2015-10-22 10:11:07.872 KST [config-pusher] INFO  o.o.c.m.s.b.i.ForwardedBackwardsCompatibleDataBroker  - ForwardedBackwardsCompatibleBroker started.
2015-10-22 10:11:07.894 KST [config-pusher] INFO  o.o.c.s.b.i.RootBindingAwareBroker  - Starting Binding Aware Broker: binding-broker-impl
2015-10-22 10:11:08.140 KST [pool-4-thread-1] INFO  o.o.m.c.t.lldp.LLDPDiscoveryProvider  - LLDPDiscoveryListener Started.
2015-10-22 10:11:08.194 KST [pool-4-thread-2] INFO  o.o.c.m.i.m.FlowCapableInventoryProvider  - Flow Capable Inventory Provider started.
2015-10-22 10:11:08.358 KST [config-pusher] INFO  o.o.c.s.c.topology.TopologyProvider  - TopologyProvider started
2015-10-22 10:11:08.468 KST [pool-4-thread-2] INFO  o.o.controller.frm.FRMActivator  - FRMActivator initialization.
2015-10-22 10:11:08.639 KST [pool-4-thread-2] INFO  o.o.c.f.i.ForwardingRulesManagerImpl  - ForwardingRulesManager has started successfull.
2015-10-22 10:11:08.639 KST [pool-4-thread-2] INFO  o.o.controller.frm.FRMActivator  - FRMActivator initialization successfull.
2015-10-22 10:11:08 KST [com.sun.jersey.core.spi.component.ProviderServices] SEVERE com.sun.jersey.core.spi.component.ProviderServices getInstances The class org.opendaylight.aaa.sts.TokenAuthFilter could not be found. This class is ignored.
2015-10-22 10:11:09 KST [com.sun.jersey.spi.inject.Errors] WARNING com.sun.jersey.spi.inject.Errors processErrorMessages The following warnings have been detected with resource and/or provider classes:
  WARNING: Parameter 2 of type org.opendaylight.yangtools.yang.data.api.Node<?> from public abstract ...
  WARNING: Parameter 1 of type org.opendaylight.yangtools.yang.data.api.Node<?> from public abstract ...
  WARNING: Parameter 2 of type org.opendaylight.yangtools.yang.data.api.Node<?> from public abstract ...
2015-10-22 10:11:14.377 KST [config-pusher] INFO  o.o.c.c.y.c.k.i.KitchenServiceModule  - KitchenService (instance org.opendaylight.controller.config.yang.config.kitchen_service.impl.KitchenServiceModule$1AutoCloseableKitchenService@4fdc6ff8) initialized.
2015-10-22 10:11:14.423 KST [config-pusher] INFO  o.o.c.c.y.c.t.i.ToasterProviderModule  - Toaster provider (instance org.opendaylight.controller.config.yang.config.toaster_provider.impl.ToasterProviderModule$1AutoCloseableToaster@53202d41) initialized.
2015-10-22 10:11:14.599 KST [Web socket server on port PortNumber [_value=8185]] INFO  o.o.c.s.s.websockets.WebSocketServer  - Web socket server started at port 8185.
2015-10-22 10:11:14.751 KST [config-pusher] INFO  o.o.c.c.y.m.s.s.StatisticsManagerModule  - StatisticsManager module initialization.
2015-10-22 10:11:14.857 KST [config-pusher] INFO  o.o.c.m.s.m.i.StatisticsManagerImpl  - Statistics Manager started successfully!
2015-10-22 10:11:14.857 KST [config-pusher] INFO  o.o.c.c.y.m.s.s.StatisticsManagerModule  - StatisticsManager started successfully.
2015-10-22 10:11:17 KST [com.sun.jersey.core.spi.component.ProviderServices] SEVERE com.sun.jersey.core.spi.component.ProviderServices getInstances The class org.opendaylight.aaa.sts.TokenAuthFilter could not be found. This class is ignored.
2015-10-22 10:11:18.140 KST [remote-connector-processing-executor-3] WARN  o.o.c.s.c.n.s.NetconfDeviceSalFacade  - RemoteDevice{controller-config}: Some rpcs from netconf device were not registered: [(urn:opendaylight:group:service?revision=2013-09-18)update-group, ...]
2015-10-22 10:11:21.721 KST [remote-connector-processing-executor-3] ERROR o.o.c.s.b.i.c.d.DomToBindingRpcForwarder  - Unable to forward RPCs for interface org.opendaylight.yang.gen.v1.urn.opendaylight.params.xml.ns.yang.controller.threadpool.impl.rev130405.ThreadpoolImplService ... (more 14 ERRORs)
2015-10-22 10:11:21.834 KST [remote-connector-processing-executor-3] INFO  o.o.c.s.c.netconf.NetconfDevice  - RemoteDevice{controller-config}: Netconf connector initialized successfully
2015-10-22 10:11:27.082 KST [ControllerI/O Thread] INFO  o.o.c.p.o.core.internal.Controller  - Switch:121.78.77.166:58514 is connected to the Controller
2015-10-22 10:11:27.170 KST [ControllerI/O Thread] INFO  o.o.c.p.o.core.internal.Controller  - Switch:121.78.77.164:41725 is connected to the Controller
```

##### 포트 충돌 현상 확인
```
osgi> 2015-10-24 18:13:07.884 KST [Start Level Event Dispatcher] INFO  o.o.c.c.s.internal.ClusterManager  - I'm a GossipRouter will listen on port 12001
2015-10-24 18:13:08.022 KST [Start Level Event Dispatcher] ERROR o.o.c.c.s.internal.ClusterManager  - GossipRouter didn't start. Exception Stack Trace
java.net.BindException: Address already in use
			...
2015-10-24 18:13:08.023 KST [Start Level Event Dispatcher] INFO  o.o.c.c.s.internal.ClusterManager  - Starting the ClusterManager
2015-10-24 18:13:09.645 KST [Start Level Event Dispatcher] INFO  o.o.c.c.i.ConfigurationService  - ConfigurationService Manager init
2015-10-24 18:13:10.112 KST [Start Level Event Dispatcher] WARN  o.o.c.u.internal.UserManager  - Network Administrator password is set to factory default. Please change the password as soon as possible.
2015-10-24 18:13:11.118 KST [ControllerI/O Thread] ERROR o.o.c.p.o.core.internal.ControllerIO  - Failed to listen on :6633, exit
2015-10-24 18:13:12 KST [org.apache.catalina.mbeans.GlobalResourcesLifecycleListener] SEVERE org.apache.catalina.mbeans.GlobalResourcesLifecycleListener createMBeans No global naming context defined for server
2015-10-24 18:13:18 KST [com.sun.jersey.core.spi.component.ProviderServices] SEVERE com.sun.jersey.core.spi.component.ProviderServices getInstances The class org.opendaylight.aaa.sts.TokenAuthFilter could not be found. This class is ignored.
2015-10-24 18:13:19 KST [com.sun.jersey.spi.inject.Errors] WARNING com.sun.jersey.spi.inject.Errors processErrorMessages The following warnings have been detected with resource and/or provider classes:
  WARNING: Parameter 2 of type org.opendaylight.yangtools.yang.data.api.Node<?> from public abstract ...
  WARNING: Parameter 1 of type org.opendaylight.yangtools.yang.data.api.Node<?> from public abstract ...
  WARNING: Parameter 2 of type org.opendaylight.yangtools.yang.data.api.Node<?> from public abstract ...
2015-10-24 18:13:25.052 KST [config-pusher] INFO  o.o.y.y.d.i.s.tree.InMemoryDataTree  - Attempting to install schema contexts
2015-10-24 18:13:25.064 KST [config-pusher] INFO  o.o.c.m.s.c.u.j.ThreadExecutorStatsMXBeanImpl  - Executor com.google.common.util.concurrent.MoreExecutors$SameThreadExecutorService@212501b7 is not supported
2015-10-24 18:13:25.065 KST [config-pusher] INFO  o.o.y.y.d.i.s.tree.InMemoryDataTree  - Attempting to install schema contexts
2015-10-24 18:13:25.066 KST [config-pusher] INFO  o.o.c.m.s.c.u.j.ThreadExecutorStatsMXBeanImpl  - Executor com.google.common.util.concurrent.MoreExecutors$SameThreadExecutorService@418bb61e is not supported
2015-10-24 18:13:25.102 KST [config-pusher] INFO  o.o.c.m.s.b.i.ForwardedBackwardsCompatibleDataBroker  - ForwardedBackwardsCompatibleBroker started.
2015-10-24 18:13:25.126 KST [config-pusher] INFO  o.o.c.s.b.i.RootBindingAwareBroker  - Starting Binding Aware Broker: binding-broker-impl
2015-10-24 18:13:25.380 KST [pool-4-thread-1] INFO  o.o.c.m.i.m.FlowCapableInventoryProvider  - Flow Capable Inventory Provider started.
2015-10-24 18:13:25.458 KST [config-pusher] INFO  o.o.c.s.c.topology.TopologyProvider  - TopologyProvider started
2015-10-24 18:13:25.500 KST [pool-4-thread-2] INFO  o.o.controller.frm.FRMActivator  - FRMActivator initialization.
2015-10-24 18:13:25.529 KST [pool-4-thread-3] INFO  o.o.m.c.t.lldp.LLDPDiscoveryProvider  - LLDPDiscoveryListener Started.
2015-10-24 18:13:25.611 KST [pool-4-thread-2] INFO  o.o.c.f.i.ForwardingRulesManagerImpl  - ForwardingRulesManager has started successfull.
2015-10-24 18:13:25.611 KST [pool-4-thread-2] INFO  o.o.controller.frm.FRMActivator  - FRMActivator initialization successfull.
2015-10-24 18:13:25 KST [com.sun.jersey.core.spi.component.ProviderServices] SEVERE com.sun.jersey.core.spi.component.ProviderServices getInstances The class org.opendaylight.aaa.sts.TokenAuthFilter could not be found. This class is ignored.
2015-10-24 18:13:25.972 KST [config-pusher] INFO  o.o.c.c.y.c.k.i.KitchenServiceModule  - KitchenService (instance org.opendaylight.controller.config.yang.config.kitchen_service.impl.KitchenServiceModule$1AutoCloseableKitchenService@72544084) initialized.
2015-10-24 18:13:26.017 KST [config-pusher] INFO  o.o.c.c.y.c.t.i.ToasterProviderModule  - Toaster provider (instance org.opendaylight.controller.config.yang.config.toaster_provider.impl.ToasterProviderModule$1AutoCloseableToaster@11658efb) initialized.
2015-10-24 18:13:26.396 KST [Web socket server on port PortNumber [_value=8185]] ERROR o.o.c.l.b.i.UncaughtExceptionPolicy  - Thread Thread[Web socket server on port PortNumber [_value=8185],5,main] died because of an uncaught exception
java.net.BindException: Address already in use
			...
2015-10-24 18:13:26.440 KST [config-pusher] INFO  o.o.c.c.y.m.s.s.StatisticsManagerModule  - StatisticsManager module initialization.
2015-10-24 18:13:26.553 KST [config-pusher] INFO  o.o.c.m.s.m.i.StatisticsManagerImpl  - Statistics Manager started successfully!
2015-10-24 18:13:26.554 KST [config-pusher] INFO  o.o.c.c.y.m.s.s.StatisticsManagerModule  - StatisticsManager started successfully.
2015-10-24 18:13:30.122 KST [remote-connector-processing-executor-3] WARN  o.o.c.s.c.n.s.NetconfDeviceSalFacade  - RemoteDevice{controller-config}: Some rpcs from netconf device were not registered: [(urn:opendaylight:group:service?revision=2013-09-18)update-group, ...]
2015-10-24 18:13:35.080 KST [remote-connector-processing-executor-3] ERROR o.o.c.s.b.i.c.d.DomToBindingRpcForwarder  - Unable to forward RPCs for interface org.opendaylight.yang.gen.v1.urn.opendaylight.params.xml.ns.yang.controller.threadpool.impl.rev130405.ThreadpoolImplService (more 13 ERRORs)
2015-10-24 18:13:35.139 KST [remote-connector-processing-executor-3] INFO  o.o.c.s.c.netconf.NetconfDevice  - RemoteDevice{controller-config}: Netconf connector initialized successfully
```
