Add-ons extend the functionality of Kubernetes.

This page lists some of the available add-ons and links to their respective
installation instructions. The list does not try to be exhaustive.

## Networking and Network Policy

* ACI provides integrated
 container networking and network security with Cisco ACI.
* Antrea operates at Layer 3/4 to provide networking and
 security services for Kubernetes, leveraging Open vSwitch as the networking
 data plane. Antrea is a CNCF project at the Sandbox level.
* Calico is a networking and network
 policy provider. Calico supports a flexible set of networking options so you
 can choose the most efficient option for your situation, including non-overlay
 and overlay networks, with or without BGP. Calico uses the same engine to
 enforce network policy for hosts, pods, and (if using Istio & Envoy)
 applications at the service mesh layer.
* Canal
 unites Flannel and Calico, providing networking and network policy.
* Cilium is a networking, observability,
 and security solution with an eBPF-based data plane. Cilium provides a
 simple flat Layer 3 network with the ability to span multiple clusters
 in either a native routing or overlay/encapsulation mode, and can enforce
 network policies on L3-L7 using an identity-based security model that is
 decoupled from network addressing. Cilium can act as a replacement for
 kube-proxy; it also offers additional, opt-in observability and security features.
 Cilium is a CNCF project at the Graduated level.
* CNI-Genie enables Kubernetes to seamlessly
 connect to a choice of CNI plugins, such as Calico, Canal, Flannel, or Weave.
 CNI-Genie is a CNCF project at the Sandbox level.
* Contiv provides configurable networking (native L3 using BGP,
 overlay using vxlan, classic L2, and Cisco-SDN/ACI) for various use cases and a rich
 policy framework. Contiv project is fully open sourced.
 The installer provides both kubeadm and
 non-kubeadm based installation options.
* Contrail,
 based on Tungsten Fabric, is an open source, multi-cloud
 network virtualization and policy management platform. Contrail and Tungsten
 Fabric are integrated with orchestration systems such as Kubernetes, OpenShift,
 OpenStack and Mesos, and provide isolation modes for virtual machines, containers/pods
 and bare metal workloads.
* Flannel is
 an overlay network provider that can be used with Kubernetes.
* Gateway API is an open source project managed by
 the SIG Network community and
 provides an expressive, extensible, and role-oriented API for modeling service networking.
* Knitter is a plugin to support multiple network
 interfaces in a Kubernetes pod.
* kube-router is an open
 source turnkey solution for Kubernetes networking with the aim to provide
 operational simplicity and high performance. It leverages the Kubernetes API,
 BGP, and Golang for the control path and Linux networking primitives (IPVS,
 nftables, etc.) for the data path. It provides a low overhead alternative and
 is used in both k0s and k3s.
* Multus is a Multi plugin for
 multiple network support in Kubernetes to support all CNI plugins
 (e.g. Calico, Cilium, Contiv, Flannel), in addition to SRIOV, DPDK, OVS-DPDK and
 VPP based workloads in Kubernetes.
* OVN-Kubernetes is a networking
 provider for Kubernetes based on OVN (Open Virtual Network),
 a virtual networking implementation that came out of the Open vSwitch (OVS) project.
 OVN-Kubernetes provides an overlay based networking implementation for Kubernetes,
 including an OVS based implementation of load balancing and network policy.
* Nodus is an OVN based CNI
 controller plugin to provide cloud native based Service function chaining(SFC).
* NSX-T Container Plug-in (NCP)
 provides integration between VMware NSX-T and container orchestrators such as
 Kubernetes, as well as integration between NSX-T and container-based CaaS/PaaS
 platforms such as Pivotal Container Service (PKS) and OpenShift.
* Nuage
 is an SDN platform that provides policy-based networking between Kubernetes
 Pods and non-Kubernetes environments with visibility and security monitoring.
* Romana is a Layer 3 networking solution for pod
 networks that also supports the NetworkPolicy API.
* Spiderpool is an underlay and RDMA
 networking solution for Kubernetes. Spiderpool is supported on bare metal, virtual machines,
 and public cloud environments.
* Terway is a suite of CNI plugins
 based on AlibabaCloud's VPC and ECS network products. It provides native VPC networking
 and network policies in AlibabaCloud environments.
* Weave Net
 provides networking and network policy, will carry on working on both sides
 of a network partition, and does not require an external database.

## Service Discovery

* CoreDNS is a flexible, extensible DNS server which can
 be installed
 as the in-cluster DNS for pods.

## Visualization &amp; Control

* Dashboard
 is a dashboard web interface for Kubernetes.
* Headlamp is an extensible Kubernetes UI that can be
 deployed in-cluster or used as a desktop application.

## Infrastructure

* KubeVirt is an add-on
 to run virtual machines on Kubernetes. Usually run on bare-metal clusters.
* The
 node problem detector
 runs on Linux nodes and reports system issues as either
 Events or
 Node conditions.

## Instrumentation

* kube-state-metrics

## Legacy Add-ons

There are several other add-ons documented in the deprecated
cluster/addons directory.

Well-maintained ones should be linked to here. PRs welcome!