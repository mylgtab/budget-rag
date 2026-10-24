This guide is a "Hello World"-style tutorial which shows how to install,
configure, and use a simple Prometheus instance. You will download and run
Prometheus locally, configure it to scrape itself and an example application,
then work with queries, rules, and graphs to use collected time
series data.

## Downloading and running Prometheus

Download the latest release of Prometheus for
your platform, then extract and run it:

[code example]

Before starting Prometheus, let's configure it.

## Configuring Prometheus to monitor itself

Prometheus collects metrics from _targets_ by scraping metrics HTTP
endpoints. Since Prometheus exposes data in the same
manner about itself, it can also scrape and monitor its own health.

While a Prometheus server that collects only data about itself is not very
useful, it is a good starting example. Save the following basic
Prometheus configuration as a file named prometheus.yml :

[code example]

For a complete specification of configuration options, see the
configuration documentation.

## Starting Prometheus

To start Prometheus with your newly created configuration file, change to the
directory containing the Prometheus binary and run:

[code example]

Prometheus should start up. You should also be able to browse to a status page
about itself at localhost:9090. Give it a couple of
seconds to collect data about itself from its own HTTP metrics endpoint.

You can also verify that Prometheus is serving metrics about itself by
navigating to its metrics endpoint:
localhost:9090/metrics

## Using the expression browser

Let us explore data that Prometheus has collected about itself. To
use Prometheus's built-in expression browser, navigate to
http://localhost:9090/query and choose the "Graph" tab.

As you can gather from localhost:9090/metrics,
one metric that Prometheus exports about itself is named
 prometheus_target_interval_length_seconds (the actual amount of time between
target scrapes). Enter the below into the expression console and then click "Execute":

[code example]

This should return a number of different time series (along with the latest value
recorded for each), each with the metric name
 prometheus_target_interval_length_seconds , but with different labels. These
labels designate different latency percentiles and target group intervals.

If we are interested only in 99th percentile latencies, we could use this
query:

[code example]

To count the number of returned time series, you could write:

[code example]

For more about the expression language, see the
expression language documentation.

## Using the graphing interface

To graph expressions, navigate to http://localhost:9090/query and use the "Graph"
tab.

For example, enter the following expression to graph the per-second rate of chunks
being created in the self-scraped Prometheus:

[code example]

Experiment with the graph range parameters and other settings.

## Starting up some sample targets

Let's add additional targets for Prometheus to scrape.

The Node Exporter is used as an example target, for more information on using it
see these instructions.

[code example]

You should now have example targets listening on http://localhost:8080/metrics,
http://localhost:8081/metrics, and http://localhost:8082/metrics.

## Configure Prometheus to monitor the sample targets

Now we will configure Prometheus to scrape these new targets. Let's group all
three endpoints into one job called node . We will imagine that the
first two endpoints are production targets, while the third one represents a
canary instance. To model this in Prometheus, we can add several groups of
endpoints to a single job, adding extra labels to each group of targets. In
this example, we will add the group="production" label to the first group of
targets, while adding group="canary" to the second.

To achieve this, add the following job definition to the scrape_configs 
section in your prometheus.yml and restart your Prometheus instance:

[code example]

Go to the expression browser and verify that Prometheus now has information
about time series that these example endpoints expose, such as node_cpu_seconds_total .

To check that Prometheus is scraping the new targets, go to
localhost:9090/targets, or open the Status 
menu and select Target health . Under the node job you should see the three
endpoints, each with a state of UP . Following the configuration above,
 localhost:8080 and localhost:8081 are labeled group="production" and
 localhost:8082 is labeled group="canary" . If an endpoint shows DOWN , make
sure the corresponding Node Exporter is still running on that port.

To confirm the metrics are available, first open a target's /metrics endpoint
directly, for example localhost:8080/metrics, to
see the raw metric names it exposes. Then enter one of them, such as 
 node_cpu_seconds_total , into the expression browser and click "Execute". This
should return one time series per CPU and mode for each instance, for example:

​[code example]

To browse every metric name that is currently available, open the query options
menu (the three-dots button to the right of the expression input) and select
 Explore metrics . 

## Configure rules for aggregating scraped data into new time series

Though not a problem in our example, queries that aggregate over thousands of
time series can get slow when computed ad-hoc. To make this more efficient,
Prometheus can prerecord expressions into new persisted
time series via configured _recording rules_. Let's say we are interested in
recording the per-second rate of cpu time ( node_cpu_seconds_total ) averaged
over all cpus per instance (but preserving the job , instance and mode 
dimensions) as measured over a window of 5 minutes. We could write this as:

[code example]

Try graphing this expression.

To record the time series resulting from this expression into a new metric
called job_instance_mode:node_cpu_seconds:avg_rate5m , create a file
with the following recording rule and save it as prometheus.rules.yml :

[code example]

To make Prometheus pick up this new rule, add a rule_files statement in your prometheus.yml . The config should now
look like this:

[code example]

Restart Prometheus with the new configuration and verify that a new time series
with the metric name job_instance_mode:node_cpu_seconds:avg_rate5m 
is now available by querying it through the expression browser or graphing it.

## Reloading configuration

As mentioned in the configuration documentation a
Prometheus instance can have its configuration reloaded without restarting the
process by using the SIGHUP signal. If you're running on Linux this can be
performed by using kill -s SIGHUP , replacing with your Prometheus
process ID.

## Shutting down your instance gracefully

While Prometheus does have recovery mechanisms in the case that there is an
abrupt process failure it is recommended to use signals or interrupts for a
clean shutdown of a Prometheus instance. On Linux, this can be done by sending
the SIGTERM or SIGINT signals to the Prometheus process. For example, you
can use kill -s , replacing with the signal name
and with the Prometheus process ID. Alternatively, you can press the
interrupt character at the controlling terminal, which by default is ^C (Control-C).