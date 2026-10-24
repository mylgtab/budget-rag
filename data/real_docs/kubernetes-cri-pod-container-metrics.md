The kubelet collects pod and
container metrics via cAdvisor. As a beta feature,
Kubernetes lets you configure the collection of pod and container
metrics via the (CRI). You
must enable the PodAndContainerStatsFromCRI 
feature gate and
use a compatible CRI implementation (containerd >= 2.2, CRI-O >= 1.31.0) to
use the CRI based collection mechanism.

## CRI Pod & Container Metrics

With PodAndContainerStatsFromCRI enabled, the kubelet polls the underlying container
runtime for pod and container stats instead of inspecting the host system directly using cAdvisor.
The benefits of relying on the container runtime for this information as opposed to direct
collection with cAdvisor include:

- Potential improved performance if the container runtime already collects this information
 during normal operations. In this case, the data can be re-used instead of being aggregated
 again by the kubelet.

- It further decouples the kubelet and the container runtime allowing collection of metrics for
 container runtimes that don't run processes directly on the host with kubelet where they are
 observable by cAdvisor (for example: container runtimes that use virtualization).

As of Kubernetes v1.37, cAdvisor-based pod and container metrics collection in the kubelet is
deprecated. CRI runtimes that do not support the required metrics will lose pod and container
level metrics collection when this feature reaches general availability (GA).

## Affected endpoints

When the feature gate is enabled, the kubelet queries the CRI runtime for pod and container
level data instead of cAdvisor. Node-level and image filesystem stats continue to be collected
from cAdvisor. The following endpoints are affected:

### Summary API ( /stats/summary )

The kubelet fetches pod and container stats from the CRI runtime instead of cAdvisor for the
Summary API. This includes CPU, memory,
network, and process stats for pods and containers.

### /metrics/cadvisor 

The kubelet queries the CRI runtime for pod and container metrics via the
 ListPodSandboxMetrics RPC and serves them on the /metrics/cadvisor endpoint. This replaces
the cAdvisor-based collection at the pod and container level while preserving the same endpoint
path and metric names. Node and machine-level metrics on this endpoint continue to be served by
cAdvisor.

## Identifying the active metrics provider

The kubelet exposes a kubelet_metrics_provider metric with a provider label set to either
 cri or cadvisor . You can use this metric to verify which source is actively providing
pod and container stats on a given node.

## Requirements

To use CRI-based metrics collection, you need:

- containerd version 2.2 or later, or CRI-O version 1.31.0 or later
- The PodAndContainerStatsFromCRI 
 feature gate enabled on the
 kubelet

CRI-O added namespace , pod , and container labels to CRI metrics on the
 /metrics/cadvisor endpoint starting in release 1.36.3. Earlier versions do not include
these labels, which may affect metric queries that rely on them to match
cAdvisor-produced metrics.

## Fallback behavior

If the CRI runtime does not report the expected metrics, the kubelet falls back to using
cAdvisor for pod and container stats collection, even when the feature gate is enabled. You
can disable the feature gate with a kubelet restart to fully revert to cAdvisor-based
collection.