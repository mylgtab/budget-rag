Kubernetes is based on a cloud native architecture and draws on advice from the
 about good practices for
cloud native information security.

Read on for an overview of how Kubernetes is designed to help you deploy a
secure cloud native platform.

## Cloud native information security

There are localized versions available of this whitepaper; if you can link to one of those
when localizing, that's even better.

The CNCF white paper
on cloud native security defines security controls and practices that are
appropriate to different _lifecycle phases_.

## _Develop_ lifecycle phase {#lifecycle-phase-develop}

- Ensure the integrity of development environments.
- Design applications following good practices for information security,
 appropriate for your context.
- Consider end user security as part of solution design.

To achieve this, you can:

1. Adopt an architecture, such as zero trust,
 that minimizes attack surfaces, even for internal threats.
1. Define a code review process that considers security concerns.
1. Build a _threat model_ of your system or application that identifies
 trust boundaries. Use that threat model to identify risks and determine
 how to treat them.
1. Incorporate advanced security automation, such as _fuzzing_ and
 security chaos engineering,
 where it's justified.

## _Distribute_ lifecycle phase {#lifecycle-phase-distribute}

- Ensure the security of the supply chain for container images you execute.
- Ensure the security of the supply chain for the cluster and other components
 that execute your application. For example, this might include an external
 database that your cloud native application uses for persistence.

To achieve this, you can:

1. Scan container images and other artifacts for known vulnerabilities.
1. Ensure that software distribution uses encryption in transit, with
 a chain of trust for the software source.
1. Adopt and follow processes to update dependencies when updates are
 available, especially in response to security announcements.
1. Use validation mechanisms such as digital certificates for supply
 chain assurance.
1. Subscribe to feeds and other mechanisms to alert you to security
 risks.
1. Restrict access to artifacts. Place container images in a
 private registry
 that only allows authorized clients to pull images.

## _Deploy_ lifecycle phase {#lifecycle-phase-deploy}

Ensure appropriate restrictions on what can be deployed, who can deploy it,
and where it can be deployed.
You can enforce measures from the _distribute_ phase, such as verifying the
cryptographic identity of container image artifacts.

You can deploy different applications and cluster components into different
. Containers
and namespaces both provide isolation mechanisms that are relevant to
information security.

When you deploy Kubernetes, you also set the foundation for your
applications' runtime environment: a Kubernetes cluster (or
multiple clusters).
That infrastructure must provide the security guarantees that higher
layers expect.

## _Runtime_ lifecycle phase {#lifecycle-phase-runtime}

The Runtime phase comprises three critical areas: access,
compute, and storage.

### Runtime protection: access {#protection-runtime-access}

The Kubernetes API is what makes your cluster work. Protecting this API is key
to providing effective cluster security.

Other pages in the Kubernetes documentation have more detail about how to set up
specific aspects of access control. The security checklist
provides suggested basic checks for your cluster.

Beyond that, securing your cluster means implementing effective
authentication and
authorization for API access. Use ServiceAccounts to
provide and manage security identities for workloads and cluster
components.

Kubernetes uses TLS to protect API traffic; make sure to deploy the cluster using
TLS (including for traffic between nodes and the control plane) and protect the
encryption keys. If you use Kubernetes' own API for
CertificateSigningRequests,
pay special attention to restricting misuse there.

### Runtime protection: compute {#protection-runtime-compute}

 provide two
things: isolation between applications and a mechanism to combine
those isolated applications to run on the same host computer. Those two
aspects—isolation and aggregation—mean that runtime security involves
identifying trade-offs and finding an appropriate balance.

Kubernetes relies on a 
to set up and run containers. The Kubernetes project does
not recommend a specific container runtime, and you should make sure that
the runtime(s) you choose meet your information security needs.

To protect your compute at runtime, you can:

1. Enforce Pod Security Standards
 for applications to help ensure they run with only the necessary privileges.
1. Run a specialized operating system on your nodes that is designed specifically
 for running containerized workloads. This is typically based on a read-only
 operating system (_immutable image_) that provides only the services
 essential for running containers.

 Container-specific operating systems help isolate system components and
 present a reduced attack surface in case of a container escape.
1. Define ResourceQuotas to
 fairly allocate shared resources, and use
 mechanisms such as LimitRanges
 to ensure that Pods specify their resource requirements.
1. Partition workloads across different nodes to improve isolation.
 Use node isolation
 mechanisms, either from Kubernetes itself or from the ecosystem, to ensure that
 Pods with different trust contexts run on separate sets of nodes.
1. Use a 
 that provides security restrictions.
1. On Linux nodes, use a Linux security module such as AppArmor
 or seccomp.

### Runtime protection: storage {#protection-runtime-storage}

To protect storage for your cluster and the applications that run there, you can:

1. Integrate your cluster with an external storage plugin that provides encryption at
 rest for volumes.
1. Enable encryption at rest for
 API objects.
1. Protect data durability using backups, and verify that you can restore them whenever needed.
1. Authenticate connections between cluster nodes and any network storage they rely
 upon.
1. Implement data encryption within your own application.

For encryption keys, generating these within specialized hardware provides
the best protection against disclosure risks. A _hardware security module_
can let you perform cryptographic operations without allowing the security
key to be copied elsewhere.

### Networking and security

You should also consider network security measures, such as
NetworkPolicy or a
service mesh.
Some network plugins for Kubernetes provide encryption for your
cluster network using technologies such as a virtual
private network (VPN) overlay.
By design, Kubernetes lets you use your own networking plugin for your
cluster. If you use managed Kubernetes, the provider may have already selected a
network plugin for you.

The network plugin you choose and the way you integrate it can have a
strong impact on the security of information in transit.

### Observability and runtime security

Kubernetes lets you extend your cluster with extra tooling. You can set up third
party solutions to help you monitor or troubleshoot your applications and the
clusters they are running. You also get some basic observability features built
in to Kubernetes itself. Your code running in containers can generate logs,
publish metrics, or provide other observability data; at deploy time, you need to
make sure your cluster provides an appropriate level of protection there.

If you set up a metrics dashboard or something similar, review the chain of components
that populate data into that dashboard, as well as the dashboard itself. Make sure
that the whole chain is designed with enough resilience and integrity protection
that you can rely on it even during an incident where your cluster might be degraded.

Where appropriate, deploy security measures below the Kubernetes layer,
such as cryptographically measured boot or authenticated distribution
of time (which helps ensure the fidelity of logs and audit records).

For a high-assurance environment, deploy cryptographic protections to ensure that
logs are both tamper-proof and confidential.

## 

### Cloud native security {#further-reading-cloud-native}

* CNCF white paper
 on cloud native security.
* CNCF white paper
 on good practices for securing a software supply chain.
* Fixing the Kubernetes clusterf\*\*k: Understanding security from the kernel up (FOSDEM 2020)
* Kubernetes Security Best Practices (Kubernetes Forum Seoul 2019)
* Towards Measured Boot Out of the Box (Linux Security Summit 2016)

### Kubernetes and information security {#further-reading-k8s}

* Kubernetes security
* Securing your cluster
* Data encryption in transit for the control plane
* Data encryption at rest
* Secrets in Kubernetes
* Controlling Access to the Kubernetes API
* Network policies for Pods
* Pod security standards
* RuntimeClasses