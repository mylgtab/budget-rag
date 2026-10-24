To use a network across multiple services, you must explicitly grant each service access by using the networks attribute within the services top-level element. The networks top-level element has additional syntax that provides more granular control.

## Examples

### Basic example

In the following example, at runtime, networks front-tier and back-tier are created and the frontend service
is connected to front-tier and back-tier networks.

[code example]

### Advanced example

[code example]

This example shows a Compose file which defines two custom networks. The proxy service is isolated from the db service, because they do not share a network in common. Only app can talk to both.

## The default network

When a Compose file doesn't declare explicit networks, Compose uses an implicit default network. Services without an explicit networks declaration are connected by Compose to this default network:

[code example]
This example is actually equivalent to:

[code example]

You can customize the default network with an explicit declaration:

[code example]

For options, see the Docker Engine docs.

## Attributes

### attachable 

If attachable is set to true , then standalone containers should be able to attach to this network, in addition to services.
If a standalone container attaches to the network, it can communicate with services and other standalone containers
that are also attached to the network.

[code example]

### driver 

 driver specifies which driver should be used for this network. Compose returns an error if the
driver is not available on the platform.

[code example]

For more information on drivers and available options, see Network drivers.

### driver_opts 

 driver_opts specifies a list of options as key-value pairs to pass to the driver. These options are
driver-dependent.

[code example]

Consult the network drivers documentation for more information.

### enable_ipv4 

 enable_ipv4 can be used to disable IPv4 address assignment.

[code example]

### enable_ipv6 

 enable_ipv6 enables IPv6 address assignment.

[code example]

### external 

If set to true :
 - external specifies that this network’s lifecycle is maintained outside of that of the application.
Compose doesn't attempt to create these networks, and returns an error if one doesn't exist.
 - All other attributes apart from name are irrelevant. If Compose detects any other attribute, it rejects the Compose file as invalid.

In the following example, proxy is the gateway to the outside world. Instead of attempting to create a network, Compose
queries the platform for an existing network called outside and connects the
 proxy service's containers to it.

[code example]

### ipam 

 ipam specifies a custom IPAM configuration. This is an object with several properties, each of which is optional:

- driver : Custom IPAM driver, instead of the default.
- config : A list with zero or more configuration elements, each containing a:
 - subnet : Subnet in CIDR format that represents a network segment
 - ip_range : Range of IPs from which to allocate container IPs
 - gateway : IPv4 or IPv6 gateway for the master subnet
 - aux_addresses : Auxiliary IPv4 or IPv6 addresses used by Network driver, as a mapping from hostname to IP
- options : Driver-specific options as a key-value mapping.

[code example]

### internal 

By default, Compose provides external connectivity to networks. internal , when set to true , lets you
create an externally isolated network.

### labels 

Add metadata to containers using labels . You can use either an array or a dictionary.

It is recommended that you use reverse-DNS notation to prevent labels from conflicting with those used by other software.

[code example]

[code example]

Compose sets com.docker.compose.project and com.docker.compose.network labels.

### name 

 name sets a custom name for the network. The name field can be used to reference networks which contain special characters.
The name is used as is and is not scoped with the project name.

[code example]

It can also be used in conjunction with the external property to define the platform network that Compose
should retrieve, typically by using a parameter so the Compose file doesn't need to hard-code runtime specific values:

[code example]

## Additional resources

For more examples, see Networking in Compose.