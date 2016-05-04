

##### VTN Neutron Enhancement
OpenDaylight Virtual Tenant Network (VTN)
=========================================

## ODL VTN overview

OpenDaylight VTN provides multi-tenant virtual network functions on
OpenDaylight controller. OpenDaylight VTN consists of two parts:
VTN Coordinator and VTN Manager.

VTN Coordinator orchestrates multiple OpenDaylight Controllers, and provides
applications with VTN API.

VTN Manager is a set of OSGi bundles running in OpenDaylight Controller.
Current VTN Manager supports only OpenFlow switches. It handles PACKET_IN
messages, sends PACKET_OUT messages, manages host information, and installs
flow entries into OpenFlow switches to provide VTN Coordinator with virtual
network functions.

The requirements for installing these two are different. Therefore, we
recommend that you install VTN Manager and VTN Coordinator in different
machines.

Please check wiki pages of OpenDaylight VTN project for more details:
https://wiki.opendaylight.org/view/OpenDaylight_Virtual_Tenant_Network_(VTN):Main

## VTN Manager

 - How to build and run VTN Manager
   https://wiki.opendaylight.org/view/OpenDaylight_Virtual_Tenant_Network_(VTN):Manager:Hacking

## VTN Coordinator

 - How to build and run VTN Coordinator
   https://wiki.opendaylight.org/view/OpenDaylight_Virtual_Tenant_Network_(VTN):Installation:VTN_Coordinator

VTN Neutron bundle will be enhanced in the VTN Manager to operate with HEAT Manager. It supports to create the virtual tenant network between multiple clouds and cooperate with Heat Manager to deploy VMs on this virtual network.



