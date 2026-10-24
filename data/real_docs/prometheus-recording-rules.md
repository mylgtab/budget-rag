## Configuring rules

Prometheus supports two types of rules which may be configured and then
evaluated at regular intervals: recording rules and alerting
rules. To include rules in Prometheus, create a file
containing the necessary rule statements and have Prometheus load the file via
the rule_files field in the Prometheus configuration.
Rule files use YAML.

The rule files can be reloaded at runtime by sending SIGHUP to the Prometheus
process. The changes are only applied if all rule files are well-formatted.

## Syntax-checking rules

To quickly check whether a rule file is syntactically correct without starting
a Prometheus server, you can use Prometheus's promtool command-line utility
tool:

[code example]

The promtool binary is part of the prometheus archive offered on the
project's download page.

When the file is syntactically valid, the checker prints a textual
representation of the parsed rules to standard output and then exits with
a 0 return status.

If there are any syntax errors or invalid input arguments, it prints an error
message to standard error and exits with a 1 return status.

## Recording rules

Recording rules allow you to precompute frequently needed or computationally
expensive expressions and save their result as a new set of time series.
Querying the precomputed result will then often be much faster than executing
the original expression every time it is needed. This is especially useful for
dashboards, which need to query the same expression repeatedly every time they
refresh.

Recording and alerting rules exist in a rule group. Rules within a group are
run sequentially at a regular interval, with the same evaluation time.
The names of recording rules must be
valid metric names.
The names of alerting rules must be
valid label values.

The syntax of a rule file is:

[code example]

A simple example rules file would be:

[code example]

### 

[code example]

### 

The syntax for recording rules is:

[code example]

The syntax for alerting rules is:

[code example]

See also the
best practices for naming metrics created by recording rules.

## Limiting alerts and series

A limit for alerts produced by alerting rules and series produced recording rules
can be configured per-group. When the limit is exceeded, _all_ series produced
by the rule are discarded, and if it's an alerting rule, _all_ alerts for
the rule, active, pending, or inactive, are cleared as well. The event will be
recorded as an error in the evaluation, and as such no stale markers are
written.

## Rule query offset
This is useful to ensure the underlying metrics have been received and stored in Prometheus. Metric availability delays are more likely to occur when Prometheus is running as a remote write target due to the nature of distributed systems, but can also occur when there's anomalies with scraping and/or short evaluation intervals.

## Failed rule evaluations due to slow evaluation

If a rule group hasn't finished evaluating before its next evaluation is supposed to start (as defined by the evaluation_interval ), the next evaluation will be skipped. Subsequent evaluations of the rule group will continue to be skipped until the initial evaluation either completes or times out. When this happens, there will be a gap in the metric produced by the recording rule. The rule_group_iterations_missed_total metric will be incremented for each missed iteration of the rule group.