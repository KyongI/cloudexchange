### Proposal for Creating an Interconnected Cloud Service

##### Abstraction
The proposal is for the advanced interconnection service that enables seamless, on-demand, direct access to multiple clouds from multiple networks.

##### Rationale
In era of cloud computing, tenants have more and more data interactions with datacenter network, and also secure connections, QoS and elastic adjustment are needed. Consequently, MPLS tunnel is a better solution to construct VPN through backbone.

Esp. in designing high availability architectures using multi-regions we need to address the following set of challenges:

- Workload Migration - ability to migrate our application environment across regions
- Data Synch - ability to migrate real time copy of the data between the two or more regions
- Network Flow - ability to enable flow of network traffic between two or more regions

##### Service Features
Orchestration Inter Cloud Connectivity with OpenDayLight and MPLS VPN 
With the advent of cloud services that require massive computing resources on-demand, the architectural model of datacenters are drifting towards geographically distributed pools of shared resources. As a result, cloud should be conceived as a multi datacenter environment that offers orchestration of per tenant virtual network which spans multiple data centers. This will provide capabilities to implement inter datacenter multi-tenant services or to migrate tenant services, such as a virtual machine, from one datacenter to another in order to exploit, for instance, geographical variations of energy costs.

MPLS technology enables the deployment of layer 2 and layer 3 VPNs between data centers with QoS guarantees to provide inter datacenter connectivity. With these capabilities, tenant virtual machines located in different datacenters can communicate transparently and also they can seamlessly move between datacenters. 

Below figure shows the high level physical topology for orchestrating the inter datacenter connectivity between multi-region using MPLS VPN to extend the L2 networks.

![orchestrating_20150902](https://cloud.githubusercontent.com/assets/12180841/9653681/3585f38a-5260-11e5-9cf0-359d626c598c.png)


 

##### Materials and Method
1.	Software Defined Networking (SDN) is an absolute requirement for building multi-tenant and multi-region OpenStack clouds.
2.	MPLS VPNaaS (MPLS VPN-as-a-Service) is a Neutron extension that introduces MPLS VPN feature set.
The following is the proposed plan for design and implementation of the MPLS VPN as a Service feature in OpenStack Networking. And this proposal refers to OpenStack Neutron/VPNaaS (IPSec VPN), OpenDayLight OVSDB OpenStack ML2 Integration.

##### Why OpenDayLight and MPLS VPN In OpenStack?
1.	OpenDaylight is an open source project focused on accelerating adoption of software-defined networking (SDN) by providing a robust SDN platform on which the industry can build and innovate. An OpenDaylight controller provides flexible management of both physical and virtual networks. The open source nature of the project and its flexible network management capabilities make it an ideal SDN platform to integrate with Neutron. 
2.	To meet users’ demands: QoS guarantee
3.	MPLS is widely supported by backbone devices: Generally, core nodes in backbone have the ability to deploy MPLS tunnels.

##### Goal and Objectives
For user’s perspective, the goals of the proposal are.
- Get data close to global applications
- Avoid latency cost of commit between sites
- Keep running during intermittent network failures between sites
- Keep running if a site fails
- Enable simple recovery when it comes back

To implement these features, we are going to enhance VTN Neutron bundle or to provide Heat Resource Plug-in.

##### VTN Neutron Enhancement
VTN Neutron bundle will be enhanced in the VTN Manager to operate with HEAT Manager. It supports to create the virtual tenant network between multiple clouds and cooperate with Heat Manager to deploy VMs on this virtual network.

##### Heat Resource Plug-in
Heat is a service to orchestrate multiple composite cloud applications using templates, through both an OpenStack-native REST API and a CloudFormation-compatible Query API. Heat allows service providers to extend the capabilities of the orchestration service by writing their own resource plug-ins. We will provide the heat resource plug-in. The plug-in creates the virtual tenant network between multiple clouds and deploys VMs on this virtual network.
