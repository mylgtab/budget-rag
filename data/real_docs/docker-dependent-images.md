To reduce push/pull time and image weight, a common practice for Compose applications is to have services
share base layers as much as possible. You typically select the same operating system base image for
all services. But you can also get one step further by sharing image layers when your images share the same
system packages. The challenge to address is then to avoid repeating the exact same Dockerfile instruction 
in all services.

For illustration, this page assumes you want all your services to be built with an alpine base
image and install the system package openssl .

## Multi-stage Dockerfile

The recommended approach is to group the shared declaration in a single Dockerfile, and use multi-stage features
so that service images are built from this shared declaration.

Dockerfile:

[code example]

Compose file:

[code example]

## Use another service's image as the base image

A popular pattern is to reuse a service image as a base image in another service.
As Compose does not parse the Dockerfile, it can't automatically detect this dependency 
between services to correctly order the build execution.

a.Dockerfile:

[code example]

b.Dockerfile:

[code example]

Compose file:

[code example]

Legacy Docker Compose v1 used to build images sequentially, which made this pattern usable
out of the box. Compose v2 uses BuildKit to optimise builds and build images in parallel 
and requires an explicit declaration.

The recommended approach is to declare the dependent base image as an additional build context:

Compose file:

[code example]

With the additional_contexts attribute, you can refer to an image built by another service without needing to explicitly name it:

b.Dockerfile:

[code example]

Compose file:

[code example]

## Build with Bake

Using Bake let you pass the complete build definition for all services
and to orchestrate build execution in the most efficient way. 

To enable this feature, run Compose with the COMPOSE_BAKE=true variable set in your environment.

[code example]

Bake can also be selected as the default builder by editing your $HOME/.docker/config.json config file:
[code example]

## Additional resources

- Docker Compose build reference
- Learn about multi-stage Dockerfiles