# Proposal for Creating an Interconnected Cloud Service

Abstraction
The proposal is for the advanced interconnection service that enables seamless, on-demand, direct access to multiple clouds from multiple networks.

Rationale
In era of cloud computing, tenants have more and more data interactions with datacenter network, and also secure connections, QoS and elastic adjustment are needed. Consequently, MPLS tunnel is a better solution to construct VPN through backbone.

Esp. in designing high availability architectures using multi-regions we need to address the following set of challenges:

	Workload Migration - ability to migrate our application environment across regions
	Data Synch - ability to migrate real time copy of the data between the two or more regions
	Network Flow - ability to enable flow of network traffic between two or more regions

Service Features
Orchestration Inter Cloud Connectivity with OpenDayLight and MPLS VPN 
With the advent of cloud services that require massive computing resources on-demand, the architectural model of datacenters are drifting towards geographically distributed pools of shared resources. As a result, cloud should be conceived as a multi datacenter environment that offers orchestration of per tenant virtual network which spans multiple data centers. This will provide capabilities to implement inter datacenter multi-tenant services or to migrate tenant services, such as a virtual machine, from one datacenter to another in order to exploit, for instance, geographical variations of energy costs.

MPLS technology enables the deployment of layer 2 and layer 3 VPNs between data centers with QoS guarantees to provide inter datacenter connectivity. With these capabilities, tenant virtual machines located in different datacenters can communicate transparently and also they can seamlessly move between datacenters. 

  
Reference Site: https://wiki.opendaylight.org/view/Release/Lithium/VTN/User_Guide/OpenStack_Support

