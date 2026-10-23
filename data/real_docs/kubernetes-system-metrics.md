System component metrics can give a better look into what is happening inside them. Metrics are
particularly useful for building dashboards and alerts.

Kubernetes components emit metrics in Prometheus format.
This format is structured plain text, designed so that people and machines can both read it.

## Metrics in Kubernetes

In most cases metrics are available on /metrics endpoint of the HTTP server. For components that
don't expose endpoint by default, it can be enabled using --bind-address flag.

Examples of those components:

* 
* 
* 
* 
* 

In a production environment you may want to configure Prometheus Server
or some other metrics scraper to periodically gather these metrics and make them available in some
kind of time series database.

Note that also exposes metrics in
 /metrics/cadvisor, /metrics/resource and /metrics/probes endpoints. Those metrics do not
have the same lifecycle.

If your cluster uses, reading metrics requires
authorization via a user, group or ServiceAccount with a ClusterRole that allows accessing
 /metrics. For example:

[code example]

## Metric lifecycle

Alpha metric → Beta metric → Stable metric → Deprecated metric → Hidden metric → Deleted metric

Alpha metrics have no stability guarantees. These metrics can be modified or deleted at any time.

Beta metrics observe a looser API contract than its stable counterparts. No labels can be removed from beta metrics during their lifetime, however, labels can be added while the metric is in the beta stage.

Stable metrics are guaranteed to not change. This means:

* A stable metric without a deprecated signature will not be deleted or renamed
* A stable metric's type will not be modified

Deprecated metrics are slated for deletion, but are still available for use.
These metrics include an annotation about the version in which they became deprecated.

For example:

* Before deprecation

 [code example]

* After deprecation

 [code example]

Hidden metrics are no longer published for scraping, but are still available for use.
A deprecated metric becomes a hidden metric after a period of time, based on its stability level:
* STABLE metrics become hidden after a minimum of 3 releases or 9 months, whichever is longer.
* BETA metrics become hidden after a minimum of 1 release or 4 months, whichever is longer.
* ALPHA metrics can be hidden or removed in the same release in which they are deprecated.

To use a hidden metric, you must enable it. For more details, refer to the Show hidden metrics section. 

Deleted metrics are no longer published and cannot be used.

## Show hidden metrics

As described above, admins can enable hidden metrics through a command-line flag on a specific
binary. This intends to be used as an escape hatch for admins if they missed the migration of the
metrics deprecated in the last release.

The flag show-hidden-metrics-for-version takes a version for which you want to show metrics
deprecated in that release. The version is expressed as x.y, where x is the major version, y is
the minor version. The patch version is not needed even though a metrics can be deprecated in a
patch release, the reason for that is the metrics deprecation policy runs against the minor release.

The flag can only take the previous minor version as its value. If you want to show all metrics hidden in the previous release, you can set the show-hidden-metrics-for-version flag to the previous version. Using a version that is too old is not allowed because it violates the metrics deprecation policy.

For example, let's assume metric A is deprecated in 1.29. The version in which metric A becomes hidden depends on its stability level:
* If metric A is ALPHA, it could be hidden in 1.29.
* If metric A is BETA, it will be hidden in 1.30 at the earliest. If you are upgrading to 1.30 and still need A, you must use the command-line flag --show-hidden-metrics-for-version=1.29.
* If metric A is STABLE, it will be hidden in 1.32 at the earliest. If you are upgrading to 1.32 and still need A, you must use the command-line flag --show-hidden-metrics-for-version=1.31.

## Component metrics

### kube-controller-manager metrics

Controller manager metrics provide important insight into the performance and health of the
controller manager. These metrics include common Go language runtime metrics such as go_routine
count and controller specific metrics such as etcd request latencies or Cloudprovider (AWS, GCE,
OpenStack) API latencies that can be used to gauge the health of a cluster.

Starting from Kubernetes 1.7, detailed Cloudprovider metrics are available for storage operations
for GCE, AWS, Vsphere and OpenStack.
These metrics can be used to monitor health of persistent volume operations.

For example, for GCE these metrics are called:

[code example]

### kube-scheduler metrics

The scheduler exposes optional metrics that reports the requested resources and the desired limits
of all running pods. These metrics can be used to build capacity planning dashboards, assess
current or historical scheduling limits, quickly identify workloads that cannot schedule due to
lack of resources, and compare actual usage to the pod's request.

The kube-scheduler identifies the resource requests and limits
configured for each Pod; when either a request or limit is non-zero, the kube-scheduler reports a
metrics timeseries. The time series is labelled by:

- namespace
- pod name
- the node where the pod is scheduled or an empty string if not yet scheduled
- priority
- the assigned scheduler for that pod
- the name of the resource (for example, cpu )
- the unit of the resource if known (for example, cores )

Once a pod reaches completion (has a restartPolicy of Never or OnFailure and is in the
 Succeeded or Failed pod phase, or has been deleted and all containers have a terminated state)
the series is no longer reported since the scheduler is now free to schedule other pods to run.
The two metrics are called kube_pod_resource_request and kube_pod_resource_limit.

The metrics are exposed at the HTTP endpoint /metrics/resources. They require
authorization for the /metrics/resources endpoint, usually granted by a
ClusterRole with the get verb for the /metrics/resources non-resource URL.

On Kubernetes 1.21 you must use the --show-hidden-metrics-for-version=1.20 
flag to expose these alpha stability metrics.

### kubelet Pressure Stall Information (PSI) metrics

When the kernel has PSI enabled (version 4.20 or later), the kubelet collects
Pressure Stall Information
(PSI) for CPU, memory and I/O usage.
The information is collected at node, pod and container level.

*Prometheus Metrics*: Exposed at the /metrics/cadvisor endpoint as cumulative counters (totals) representing the total stall time in seconds. The metrics are exposed at this endpoint with the following names: 

[code example]
*Summary API*: Exposed at the /stats/summary endpoint, providing both the cumulative totals and the moving averages ( avg10, avg60, avg300 ) in a JSON format. These averages represent the percentage of time that tasks were stalled on a resource over the respective 10-second, 60-second, and 5-minute intervals. 

These metrics are also natively exported through the node's respective file in /proc/pressure/ -- cpu, memory, and io in the following format: 

[code example]

How can these metrics be interpreted together? Take for example the following query from the Summary API: 
 kubectl get --raw "/api/v1/nodes/$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')/proxy/stats/summary" | jq '.pods[].containers[] | select(.name=="") | {name, cpu:.cpu.psi, memory:.memory.psi, io:.io.psi}'. 
This returns the information in a json format as such. 

[code example]

Here is a simple spike scenario. The cpu.some avg10 value of 0.74 indicates that in the last 10 seconds, at least one task in this container was stalled on the CPU for 0.74% of the time (0.0074 seconds or 74 milliseconds). Because avg10 (0.74) is significantly higher than avg300 (0.21) on the same resource, this suggests a recent surge in resource contention rather than a sustained long-term bottleneck. If monitored continuously and the avg300 metrics increase as well, we can diagnose a more serious, lasting issue!

Additionally, notice how in this example cpu.some shows pressure, while cpu.full remains at 0.00. This tells us that while some processes were delayed waiting for CPU time, the container as a whole was still making progress. A non-zero full value would indicate that all non-idle tasks were stalled simultaneously, a much bigger problem.
Although not as human-readable, the total value of 35232438 represents the cumulative stall time in microseconds, that allow latency spike detection that otherwise may not show in the averages. They are also useful for monitoring systems, like Prometheus, to calculate precise rates of increase over specific time windows.
As a final note, when observing high I/O Pressure alongside low Memory Pressure, it can indicate that the application is waiting on disk throughput rather than failing due to a lack of available RAM. The node is not over-committed on memory, and a different diagnosis for disk consumption can be investigated. 

PSI metrics unlock a more robust way to monitor realitime resource contention at all levels for every cgroup, opening up the opportunity to dynamically handle workloads across the system. You can read more about the PSI metrics in Understand PSI Metrics.

#### Requirements

Pressure Stall Information requires:

- Linux kernel versions 4.20 or later.
- cgroup v2

## Disabling metrics

You can explicitly turn off metrics via command line flag --disabled-metrics. This may be
desired if, for example, a metric is causing a performance problem. The input is a list of
disabled metrics (i.e. --disabled-metrics=metric1,metric2 ).

## Metric cardinality enforcement

Metrics with unbounded dimensions could cause memory issues in the components they instrument. To
limit resource use, you can use the --allow-metric-labels command line option to dynamically
configure an allow-list of label values for a metric.

In alpha stage, the flag can only take in a series of mappings as metric label allow-list.
Each mapping is of the format,= where 
 is a comma-separated list of acceptable label names.
 
The overall format looks like:

[code example]

Here is an example:

[code example]

In addition to specifying this from the CLI, this can also be done within a configuration file. You
can specify the path to that configuration file using the --allow-metric-labels-manifest command
line argument to a component. Here's an example of the contents of that configuration file:

[code example]

Additionally, the cardinality_enforcement_unexpected_categorizations_total meta-metric records the
count of unexpected categorizations during cardinality enforcement, that is, whenever a label value
is encountered that is not allowed with respect to the allow-list constraints.

## 

* Read about the Prometheus text format
 for metrics
* See the list of stable Kubernetes metrics
* Read about the Kubernetes deprecation policy