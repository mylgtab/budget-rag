If you create a docker-container or kubernetes builder with Buildx, you can
apply a custom BuildKit configuration by passing the
 --buildkitd-config flag
to the docker buildx create command.

## Registry mirror

You can define a registry mirror to use for your builds. Doing so redirects
BuildKit to pull images from a different hostname. The following steps exemplify
defining a mirror for docker.io (Docker Hub) to mirror.gcr.io .

1. Create a TOML at /etc/buildkitd.toml with the following content:

 [code example]

 > [!NOTE]
 >
 > debug = true turns on debug requests in the BuildKit daemon, which logs a
 > message that shows when a mirror is being used.

2. Create a docker-container builder that uses this BuildKit configuration:

 [code example]

3. Build an image:

 [code example]

The BuildKit logs for this builder now shows that it uses the GCR mirror. You
can tell by the fact that the response messages include the x-goog-* HTTP
headers.

[code example]

[code example]

## Setting registry certificates

If you specify registry certificates in the BuildKit configuration, the daemon
copies the files into the container under /etc/buildkit/certs . The following
steps show adding a self-signed registry certificate to the BuildKit
configuration.

1. Add the following configuration to /etc/buildkitd.toml :

 [code example]

 This tells the builder to push images to the myregistry.com registry using
 the certificates in the specified location ( /etc/certs ).

2. Create a docker-container builder that uses this configuration:

 [code example]

3. Inspect the builder's configuration file ( /etc/buildkit/buildkitd.toml ), it
 shows that the certificate configuration is now configured in the builder.

 [code example]

 [code example]

4. Verify that the certificates are inside the container:

 [code example]

Now you can push to the registry using this builder, and it will authenticate
using the certificates:

[code example]

## CNI networking

CNI networking for builders can be useful for dealing with network port
contention during concurrent builds.

### Bridge networking

The BuildKit image ships with a built-in bridge network provider that uses a
minimal set of bundled CNI plugins, so you don't need to build a custom image
or supply your own CNI configuration. To use it, set the worker network mode to
 bridge when you create the builder:

[code example]

BuildKit creates a buildkit0 bridge with a default subnet of 10.10.0.0/16 ,
and cleans up the bridge automatically when the daemon shuts down.

### Custom CNI configuration

For more control over networking, build a custom BuildKit image with your own
CNI configuration and plugins.

The following Dockerfile example shows a custom BuildKit image with CNI support.
It uses the CNI config for integration tests
in BuildKit as an example. Feel free to include your own CNI configuration.

[code example]

Now you can build this image, and create a builder instance from it using
the --driver-opt image option:

[code example]

## Resource limiting

### Max parallelism

You can limit the parallelism of the BuildKit solver, which is particularly useful
for low-powered machines, using a BuildKit configuration
while creating a builder with the --buildkitd-config flag.

[code example]

Now you can create a docker-container builder
that will use this BuildKit configuration to limit parallelism.

[code example]

### TCP connection limit

TCP connections are limited to 4 simultaneous connections per registry for
pulling and pushing images, plus one additional connection dedicated to metadata
requests. This connection limit prevents your build from getting stuck while
pulling images. The dedicated metadata connection helps reduce the overall build
time.

More information: moby/buildkit#2259