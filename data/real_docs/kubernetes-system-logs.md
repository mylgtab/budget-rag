System component logs record events happening in cluster, which can be very useful for debugging.
You can configure log verbosity to see more or less detail.
Logs can be as coarse-grained as showing errors within a component, or as fine-grained as showing
step-by-step traces of events (like HTTP access logs, pod state changes, controller actions, or
scheduler decisions).

In contrast to the command line flags described here, the *log
output* itself does *not* fall under the Kubernetes API stability guarantees:
individual log entries and their formatting may change from one release
to the next!

## Klog

klog is the Kubernetes logging library. klog
generates log messages for the Kubernetes system components.

Kubernetes is in the process of simplifying logging in its components.
The following klog command line flags
are deprecated
starting with Kubernetes v1.23 and removed in Kubernetes v1.26:

- --add-dir-header 
- --alsologtostderr 
- --log-backtrace-at 
- --log-dir 
- --log-file 
- --log-file-max-size 
- --logtostderr 
- --one-output 
- --skip-headers 
- --skip-log-headers 
- --stderrthreshold 

Output will always be written to stderr, regardless of the output format. Output redirection is
expected to be handled by the component which invokes a Kubernetes component. This can be a POSIX
shell or a tool like systemd.

In some cases, for example a distroless container or a Windows system service, those options are
not available. Then the
 kube-log-runner 
binary can be used as wrapper around a Kubernetes component to redirect
output. A prebuilt binary is included in several Kubernetes base images under
its traditional name as /go-runner and as kube-log-runner in server and
node release archives.

This table shows how kube-log-runner invocations correspond to shell redirection:

| Usage | POSIX shell (such as bash) | kube-log-runner |

| Merge stderr and stdout, write to stdout | 2>&1 | kube-log-runner (default behavior) |
| Redirect both into log file | 1>>/tmp/log 2>&1 | kube-log-runner -log-file=/tmp/log |
| Copy into log file and to stdout | 2>&1 \| tee -a /tmp/log | kube-log-runner -log-file=/tmp/log -also-stdout |
| Redirect only stdout into log file | >/tmp/log | kube-log-runner -log-file=/tmp/log -redirect-stderr=false |

### Klog output

An example of the traditional klog native format:

[code example]

The message string may contain line breaks:

[code example]

### Structured Logging

Migration to structured log messages is an ongoing process. Not all log messages are structured in
this version. When parsing log files, you must also handle unstructured log messages.

Log formatting and value serialization are subject to change.

Structured logging introduces a uniform structure in log messages allowing for programmatic
extraction of information. You can store and process structured logs with less effort and cost.
The code which generates a log message determines whether it uses the traditional unstructured
klog output or structured logging.

The default formatting of structured log messages is as text, with a format that is backward
compatible with traditional klog:

[code example]

Example:

[code example]

Strings are quoted. Other values are formatted with
 %+v, which may cause log messages to
continue on the next line depending on the data.

[code example]

### Contextual Logging

Contextual logging builds on top of structured logging. It is primarily about
how developers use logging calls: code based on that concept is more flexible
and supports additional use cases as described in the Contextual Logging
KEP.

If developers use additional functions like WithValues or WithName in
their components, then log entries contain additional information that gets
passed into functions by their caller.

For Kubernetes, this is gated behind the ContextualLogging 
feature gate and is
enabled by default. The infrastructure for this was added in 1.24 without
modifying components. The
 component-base/logs/example 
command demonstrates how to use the new logging calls and how a component
behaves that supports contextual logging.

[code example]

The logger key and foo="bar" were added by the caller of the function
which logs the runtime message and duration="1m0s" value, without having to
modify that function.

With contextual logging disable, WithValues and WithName do nothing and log
calls go through the global klog logger. Therefore this additional information
is not in the log output anymore:

[code example]

### JSON log format

JSON output does not support many standard klog flags. For list of unsupported klog flags, see the
Command line tool reference.

Not all logs are guaranteed to be written in JSON format (for example, during process start).
If you intend to parse logs, make sure you can handle log lines that are not JSON as well.

Field names and JSON serialization are subject to change.

The --logging-format=json flag changes the format of logs from klog native format to JSON format.
Example of JSON log format (pretty printed):

[code example]

Keys with special meaning:

* ts - timestamp as Unix time (required, float)
* v - verbosity (only for info and not for error messages, int)
* err - error string (optional, string)
* msg - message (required, string)

List of components currently supporting JSON format:

* 
* 
* 
* 

### Log verbosity level

The -v flag controls log verbosity. Increasing the value increases the number of logged events.
Decreasing the value decreases the number of logged events. Increasing verbosity settings logs
increasingly less severe events. A verbosity setting of 0 logs only critical events.

### Log location

There are two types of system components: those that run in a container and those
that do not run in a container. For example:

* The Kubernetes scheduler and kube-proxy run in a container.
* The kubelet and 
 do not run in containers.

On machines with systemd, the kubelet and container runtime write to journald.
Otherwise, they write to.log files in the /var/log directory.
System components inside containers always write to.log files in the /var/log directory,
bypassing the default logging mechanism.
Similar to the container logs, you should rotate system component logs in the /var/log directory.
In Kubernetes clusters created by the kube-up.sh script, log rotation is configured by the logrotate tool.
The logrotate tool rotates logs daily, or once the log size is greater than 100MB.

## Log query

The Log Query feature can help debugging issues in both Linux and Windows 
nodes. Introduced in Kubernetes v1.27, the feature allows viewing logs of 
services running on the node. To use the feature, ensure that the kubelet 
configuration options enableSystemLogHandler and enableSystemLogQuery 
are both set to _true_ for the target node.

In Kubernetes v1.36 this feature graduated to stable and the NodeLogQuery feature gate 
is now locked to _true_, hence the feature gate is enabled by default, leaving
 enableSystemLogHandler as the only option required to enable or disable the
Log Query feature. 

 enableSystemLogHandler defaults to _false_ and is recommended to be left 
disabled unless actively debugging.

Granting permissions to nodes/proxy (even just get permission) also
authorizes access to powerful kubelet APIs that can be used to execute commands
in any container running on the node, so be careful about how you manage them.
See Kubelet authentication/authorization
for more information.

On Linux, the assumption is that service logs are available via _journald_. On 
Windows the assumption is that service logs are available in the application log
provider. On both operating systems, logs are also available by reading files
within /var/log/.

Provided you are authorized to interact with node objects, you can try out this feature on all your nodes or
just a subset. Here is an example to retrieve the kubelet service logs from a node:

[code example]

You can also fetch files, provided that the files are in a directory that the kubelet allows for log
fetches. For example, you can fetch a log from /var/log on a Linux node:

[code example]

The kubelet uses heuristics to retrieve logs. This helps if you are not aware whether a given system service is
writing logs to the operating system's native logger like journald or to a log file in /var/log/. The heuristics
first checks the native logger and if that is not available attempts to retrieve the first logs from
 /var/log/ or /var/log/.log or /var/log//.log.

The complete list of options that can be used are:

| Option | Description |

| boot | boot show messages from a specific system boot |
| pattern | pattern filters log entries by the provided PERL-compatible regular expression |
| query | query specifies services(s) or files from which to return logs (required) |
| sinceTime | an RFC3339 timestamp from which to show logs (inclusive) |
| untilTime | an RFC3339 timestamp until which to show logs (inclusive) |
| tailLines | specify how many lines from the end of the log to retrieve; the default is to fetch the whole log |

Example of a more complex query:

[code example]

## 

* Read about the Kubernetes Logging Architecture
* Read about Structured Logging
* Read about Contextual Logging
* Read about deprecation of klog flags
* Read about the Conventions for logging severity
* Read about Log Query