Prometheus supports templating in the annotations and labels of alerts,
as well as in served console pages. Templates have the ability to run
queries against the local database, iterate over data, use conditionals,
format data, etc. The Prometheus templating language is based on the Go
templating system.

## Simple alert field templates

[code example]

Alert field templates will be executed during every rule iteration for each
alert that fires, so keep any queries and templates lightweight. If you have a
need for more complicated templates for alerts, it is recommended to link to a
console instead.

## Simple iteration

This displays a list of instances, and whether they are up:

[code example]

The special . variable contains the value of the current sample for each loop iteration.

## Display one value

[code example]

Go and Go's templating language are both strongly typed, so one must check that
samples were returned to avoid an execution error. For example this could
happen if a scrape or rule evaluation has not run yet, or a host was down.

The included prom_query_drilldown template handles this, allows for
formatting of results, and linking to the expression browser.

## Using console URL parameters

[code example]

If accessed as console.html?instance=hostname , .Params.instance will evaluate to hostname .

## Advanced iteration

[code example]

Here we iterate over all network devices and display the network traffic for each.

As the range action does not specify a variable, .Params.instance is not
available inside the loop as . is now the loop variable.

## Defining reusable templates

Prometheus supports defining templates that can be reused. This is particularly
powerful when combined with
console library support, allowing
sharing of templates across consoles.

[code example]

Templates are limited to one argument. The args function can be used to wrap multiple arguments.

[code example]