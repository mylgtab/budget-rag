Distributed systems often have a need for _leases_, which provide a mechanism to lock shared resources
and coordinate activity between members of a set.
In Kubernetes, the lease concept is represented by Lease
objects in the coordination.k8s.io ,
which are used for system-critical capabilities such as node heartbeats and component-level leader election.

## Node heartbeats {#node-heart-beats}

Kubernetes uses the Lease API to communicate kubelet node heartbeats to the Kubernetes API server.
For every Node , there is a Lease object with a matching name in the kube-node-lease 
namespace. Under the hood, every kubelet heartbeat is an update request to this Lease object, updating
the spec.renewTime field for the Lease. The Kubernetes control plane uses the time stamp of this field
to determine the availability of this Node .

See Node Lease objects for more details.

## Leader election

Kubernetes also uses Leases to ensure only one instance of a component is running at any given time.
This is used by control plane components like kube-controller-manager and kube-scheduler in
HA configurations, where only one instance of the component should be actively running while the other
instances are on stand-by.

Read coordinated leader election
to learn about how Kubernetes builds on the Lease API to select which component instance
acts as leader.

### Kube controller manager lock release on exit

When the ControllerManagerReleaseLeaderElectionLockOnExit feature gate is enabled,
the kube-controller-manager actively releases its leader election lock during
leader transitions, rather than waiting for the lock's TTL to expire. This allows
a new leader to be elected more quickly, reducing leader transition latency.

## API server identity

Starting in Kubernetes v1.26, each kube-apiserver uses the Lease API to publish its identity to the
rest of the system. While not particularly useful on its own, this provides a mechanism for clients to
discover how many instances of kube-apiserver are operating the Kubernetes control plane.
Existence of kube-apiserver leases enables future capabilities that may require coordination between
each kube-apiserver.

You can inspect Leases owned by each kube-apiserver by checking for lease objects in the kube-system namespace
with the name apiserver- . Alternatively you can use the label selector apiserver.kubernetes.io/identity=kube-apiserver :

[code example]
[code example]

The SHA256 hash used in the lease name is based on the OS hostname as seen by that API server. Each kube-apiserver should be
configured to use a hostname that is unique within the cluster. New instances of kube-apiserver that use the same hostname
will take over existing Leases using a new holder identity, as opposed to instantiating new Lease objects. You can check the
hostname used by kube-apiserver by checking the value of the kubernetes.io/hostname label:

[code example]
[code example]

Expired leases from kube-apiservers that no longer exist are garbage collected by new kube-apiservers after 1 hour.

You can disable API server identity leases by disabling the APIServerIdentity 
feature gate.

## Workloads {#custom-workload}

Your own workload can define its own use of Leases. For example, you might run a custom
 where a primary or leader member
performs operations that its peers do not. You define a Lease so that the controller replicas can select
or elect a leader, using the Kubernetes API for coordination.
If you do use a Lease, it's a good practice to define a name for the Lease that is obviously linked to
the product or component. For example, if you have a component named Example Foo, use a Lease named
 example-foo .

If a cluster operator or another end user could deploy multiple instances of a component, select a name
prefix and pick a mechanism (such as hash of the name of the Deployment) to avoid name collisions
for the Leases.

You can use another approach so long as it achieves the same outcome: different software products do
not conflict with one another.