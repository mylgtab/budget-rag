Kubernetes runs your 
by placing into Pods to run on _Nodes_.
A node may be a virtual or physical machine, depending on the cluster. Each node
is managed by the

and contains the services necessary to run
.

Typically you have several nodes in a cluster; in a learning or resource-limited
environment, you might have only one node.

The components on a node include the
, a
, and the
.

## Management

There are two main ways to have Nodes added to the
:

1. The kubelet on a node self-registers to the control plane
2. You (or another human user) manually add a Node object

After you create a Node,
or the kubelet on a node self-registers, the control plane checks whether the new Node object
is valid. For example, if you try to create a Node from the following JSON manifest:

[code example]

Kubernetes creates a Node object internally (the representation). Kubernetes checks
that a kubelet has registered to the API server that matches the metadata.name 
field of the Node. If the node is healthy (i.e. all necessary services are running),
then it is eligible to run a Pod. Otherwise, that node is ignored for any cluster activity
until it becomes healthy.

Kubernetes keeps the object for the invalid Node and continues checking to see whether
it becomes healthy.

You, or a, must explicitly
delete the Node object to stop that health checking.

The name of a Node object must be a valid
DNS subdomain name.

### Node name uniqueness

The name identifies a Node. Two Nodes
cannot have the same name at the same time. Kubernetes also assumes that a resource with the same
name is the same object. In the case of a Node, it is implicitly assumed that an instance using the
same name will have the same state (e.g. network settings, root disk contents) and attributes like
node labels. This may lead to inconsistencies if an instance was modified without changing its name.
If the Node needs to be replaced or updated significantly, the existing Node object needs to be
removed from API server first and re-added after the update.

### Self-registration of Nodes

When the kubelet flag --register-node is true (the default), the kubelet will attempt to
register itself with the API server. This is the preferred pattern, used by most distros.

For self-registration, the kubelet is started with the following options:

- --kubeconfig - Path to credentials to authenticate itself to the API server.
- --cloud-provider - How to talk to a 
 to read metadata about itself.
- --register-node - Automatically register with the API server.
- --register-with-taints - Register the node with the given list of
 (comma separated =: ).

 No-op if register-node is false.
- --node-ip - Optional comma-separated list of the IP addresses for the node.
 You can only specify a single address for each address family.
 For example, in a single-stack IPv4 cluster, you set this value to be the IPv4 address that the
 kubelet should use for the node.
 See configure IPv4/IPv6 dual stack
 for details of running a dual-stack cluster.

 If you don't provide this argument, the kubelet uses the node's default IPv4 address, if any;
 if the node has no IPv4 addresses then the kubelet uses the node's default IPv6 address.
- --node-labels - to add when registering the node
 in the cluster (see label restrictions enforced by the
 NodeRestriction admission plugin).
- --node-status-update-frequency - Specifies how often kubelet posts its node status to the API server.

When the Node authorization mode and
NodeRestriction admission plugin
are enabled, kubelets are only authorized to create/modify their own Node resource.

As mentioned in the Node name uniqueness section,
when Node configuration needs to be updated, it is a good practice to re-register
the node with the API server. For example, if the kubelet is being restarted with
a new set of --node-labels, but the same Node name is used, the change will
not take effect, as labels are only set (or modified) upon Node registration with the API server.

Pods already scheduled on the Node may misbehave or cause issues if the Node
configuration will be changed on kubelet restart. For example, an already running
Pod may be tainted against the new labels assigned to the Node, while other
Pods, that are incompatible with that Pod will be scheduled based on this new
label. Node re-registration ensures all Pods will be drained and properly
re-scheduled.

### Manual Node administration

You can create and modify Node objects using
.

When you want to create Node objects manually, set the kubelet flag --register-node=false.

You can modify Node objects regardless of the setting of --register-node.
For example, you can set labels on an existing Node or mark it unschedulable.

You can set optional node role(s) for nodes by adding one or more node-role.kubernetes.io/: labels to the node where characters of 
are limited by the syntax rules for labels.

Kubernetes ignores the label value for node roles; by convention, you can set it to the same string you used for the node role in the label key.

You can use labels on Nodes in conjunction with node selectors on Pods to control
scheduling. For example, you can constrain a Pod to only be eligible to run on
a subset of the available nodes.

Marking a node as unschedulable prevents the scheduler from placing new pods onto
that Node but does not affect existing Pods on the Node. This is useful as a
preparatory step before a node reboot or other maintenance.

To mark a Node unschedulable, run:

[code example]

See Safely Drain a Node
for more details.

Pods that are part of a tolerate
being run on an unschedulable Node. DaemonSets typically provide node-local services
that should run on the Node even if it is being drained of workload applications.

## Node status

A Node's status contains the following information:

* Addresses
* Conditions
* Capacity and Allocatable
* Info

You can use kubectl to view a Node's status and other details:

[code example]

See Node Status for more details.

## Node heartbeats

Heartbeats, sent by Kubernetes nodes, help your cluster determine the
availability of each node, and to take action when failures are detected.

For nodes there are two forms of heartbeats:

* Updates to the.status of a Node.
* Lease objects
 within the kube-node-lease 
.
 Each Node has an associated Lease object.

## Node controller

The node is a
Kubernetes control plane component that manages various aspects of nodes.

The node controller has multiple roles in a node's life. The first is assigning a
CIDR block to the node when it is registered (if CIDR assignment is turned on).

The second is keeping the node controller's internal list of nodes up to date with
the cloud provider's list of available machines. When running in a cloud
environment and whenever a node is unhealthy, the node controller asks the cloud
provider if the VM for that node is still available. If not, the node
controller deletes the node from its list of nodes.

The third is monitoring the nodes' health. The node controller is
responsible for:

- In the case that a node becomes unreachable, updating the Ready condition
 in the Node's.status field. In this case the node controller sets the
 Ready condition to Unknown.
- If a node remains unreachable: triggering
 API-initiated eviction
 for all of the Pods on the unreachable node. By default, the node controller
 waits 5 minutes between marking the node as Unknown and submitting
 the first eviction request.

By default, the node controller checks the state of each node every 5 seconds.
This period can be configured using the --node-monitor-period flag on the
 kube-controller-manager component.

### Rate limits on eviction

In most cases, the node controller limits the eviction rate to
 --node-eviction-rate (default 0.1) per second, meaning it won't evict pods
from more than 1 node per 10 seconds.

The node eviction behavior changes when a node in a given availability zone
becomes unhealthy. The node controller checks what percentage of nodes in the zone
are unhealthy (the Ready condition is Unknown or False ) at the same time:

- If the fraction of unhealthy nodes is at least --unhealthy-zone-threshold 
 (default 0.55), then the eviction rate is reduced.
- If the cluster is small (i.e. has less than or equal to
 --large-cluster-size-threshold nodes - default 50), then evictions are stopped.
- Otherwise, the eviction rate is reduced to --secondary-node-eviction-rate 
 (default 0.01) per second.

The reason these policies are implemented per availability zone is because one
availability zone might become partitioned from the control plane while the others remain
connected. If your cluster does not span multiple cloud provider availability zones,
then the eviction mechanism does not take per-zone unavailability into account.

A key reason for spreading your nodes across availability zones is so that the
workload can be shifted to healthy zones when one entire zone goes down.
Therefore, if all nodes in a zone are unhealthy, then the node controller evicts at
the normal rate of --node-eviction-rate. The corner case is when all zones are
completely unhealthy (none of the nodes in the cluster are healthy). In such a
case, the node controller assumes that there is some problem with connectivity
between the control plane and the nodes, and doesn't perform any evictions.
(If there has been an outage and some nodes reappear, the node controller does
evict pods from the remaining nodes that are unhealthy or unreachable).

The node controller is also responsible for evicting pods running on nodes with
 NoExecute taints, unless those pods tolerate that taint.
The node controller also adds 
corresponding to node problems like node unreachable or not ready. This means
that the scheduler won't place Pods onto unhealthy nodes.

## Resource capacity tracking {#node-capacity}

Node objects track information about the Node's resource capacity: for example, the amount
of memory available and the number of CPUs.
Nodes that self register report their capacity during
registration. If you manually add a Node, then
you need to set the node's capacity information when you add it.

The Kubernetes ensures that
there are enough resources for all the Pods on a Node. The scheduler checks that the sum
of the requests of containers on the node is no greater than the node's capacity.
That sum of requests includes all containers managed by the kubelet, but excludes any
containers started directly by the container runtime, and also excludes any
processes running outside of the kubelet's control.

If you want to explicitly reserve resources for non-Pod processes, see
reserve resources for system daemons.

## Node topology

If you have enabled the TopologyManager 
feature gate, then
the kubelet can use topology hints when making resource assignment decisions.
See Control Topology Management Policies on a Node
for more information.

## 

Learn more about the following:

* Components that make up a node.
* API definition for Node.
* Node
 section of the architecture design document.
* Graceful/non-graceful node shutdown.
* Node autoscaling to
 manage the number and size of nodes in your cluster.
* Taints and Tolerations.
* Node Resource Managers.
* Resource Management for Windows nodes.