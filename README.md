### Virtual-Tenant-Network-Orchestrator

##### Rationale
In era of cloud computing, tenants have more and more data interactions with datacenter network, and also secure connections, QoS and elastic adjustment are needed. Consequently, MPLS tunnel is a better solution to construct VPN through backbone.

Esp. in designing high availability architectures using multi-regions we need to address the following set of challenges:

- Workload Migration - ability to migrate our application environment across regions
- Data Synch - ability to migrate real time copy of the data between the two or more regions
- Network Flow - ability to enable flow of network traffic between two or more regions

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


