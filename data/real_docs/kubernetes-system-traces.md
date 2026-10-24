System component traces record the latency of and relationships between operations in the cluster.

Kubernetes components emit traces using the
OpenTelemetry Protocol
with the gRPC exporter and can be collected and routed to tracing backends using an
OpenTelemetry Collector.

## Trace Collection

Kubernetes components have built-in gRPC exporters for OTLP to export traces, either with an OpenTelemetry Collector, 
or without an OpenTelemetry Collector.

For a complete guide to collecting traces and using the collector, see
Getting Started with the OpenTelemetry Collector.
However, there are a few things to note that are specific to Kubernetes components.

By default, Kubernetes components export traces using the grpc exporter for OTLP on the
IANA OpenTelemetry port, 4317.
As an example, if the collector is running as a sidecar to a Kubernetes component,
the following receiver configuration will collect spans and log them to standard output:

[code example]

To directly emit traces to a backend without utilizing a collector, 
specify the endpoint field in the Kubernetes tracing configuration file with the desired trace backend address. 
This method negates the need for a collector and simplifies the overall structure.

For trace backend header configuration, including authentication details, environment variables can be used with OTEL_EXPORTER_OTLP_HEADERS , 
see OTLP Exporter Configuration.

Additionally, for trace resource attribute configuration such as Kubernetes cluster name, namespace, Pod name, etc., 
environment variables can also be used with OTEL_RESOURCE_ATTRIBUTES , see OTLP Kubernetes Resource.

## Component traces

### kube-apiserver traces

The kube-apiserver generates spans for incoming HTTP requests, and for outgoing requests
to webhooks, etcd, and re-entrant requests. It propagates the
W3C Trace Context with outgoing requests
but does not make use of the trace context attached to incoming requests,
as the kube-apiserver is often a public endpoint.

#### Enabling tracing in the kube-apiserver

To enable tracing, provide the kube-apiserver with a tracing configuration file
with --tracing-config-file= . This is an example config that records
spans for 1 in 10000 requests, and uses the default OpenTelemetry endpoint:

[code example]

For more information about the TracingConfiguration struct, see
API server config API (v1).

### kubelet traces

The kubelet CRI interface and authenticated http servers are instrumented to generate
trace spans. As with the apiserver, the endpoint and sampling rate are configurable.
Trace context propagation is also configured. A parent span's sampling decision is always respected.
A provided tracing configuration sampling rate will apply to spans without a parent.
Enabled without a configured endpoint, the default OpenTelemetry Collector receiver address of "localhost:4317" is set.

#### Enabling tracing in the kubelet

To enable tracing, apply the tracing configuration.
This is an example snippet of a kubelet config that records spans for 1 in 10000 requests, and uses the default OpenTelemetry endpoint:

[code example]

If the samplingRatePerMillion is set to one million ( 1000000 ), then every
span will be sent to the exporter.

The kubelet in Kubernetes v collects spans from
the garbage collection, pod synchronization routine as well as every gRPC
method. The kubelet propagates trace context with gRPC requests so that
container runtimes with trace instrumentation, such as CRI-O and containerd,
can associate their exported spans with the trace context from the kubelet.
The resulting traces will have parent-child links between kubelet and
container runtime spans, providing helpful context when debugging node
issues.

Please note that exporting spans always comes with a small performance overhead
on the networking and CPU side, depending on the overall configuration of the
system. If there is any issue like that in a cluster which is running with
tracing enabled, then mitigate the problem by either reducing the
 samplingRatePerMillion or disabling tracing completely by removing the
configuration.

## Stability

Tracing instrumentation is still under active development, and may change
in a variety of ways. This includes span names, attached attributes,
instrumented endpoints, etc. Until this feature graduates to stable,
there are no guarantees of backwards compatibility for tracing instrumentation.

## 

* Read about Getting Started with the OpenTelemetry Collector
* Read about OTLP Exporter Configuration