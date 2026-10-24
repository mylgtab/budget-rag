## Using pre-compiled binaries

We provide precompiled binaries for most official Prometheus components. Check
out the download section for a list of all
available versions.

## From source

For building Prometheus components from source, see the Makefile targets in
the respective repository.

## Using Docker

All Prometheus services are available as Docker images on
Quay.io or
Docker Hub.

Running Prometheus on Docker is as simple as docker run -p 9090:9090
prom/prometheus . This starts Prometheus with a sample
configuration and exposes it on port 9090.

The Prometheus image uses a volume to store the actual metrics. For
production deployments it is highly recommended to use a
named volume
to ease managing the data on Prometheus upgrades.

### Setting command line parameters

The Docker image is started with a number of default command line parameters, which
can be found in the Dockerfile (adjust the link to correspond with the version in use).

If you want to add extra command line parameters to the docker run command,
you will need to re-add these yourself as they will be overwritten.

### Volumes & bind-mount

To provide your own configuration, there are several options. Here are
two examples.

Bind-mount your prometheus.yml from the host by running:

[code example]

Or bind-mount the directory containing prometheus.yml onto
 /etc/prometheus by running:

[code example]

### Save your Prometheus data

Prometheus data is stored in /prometheus dir inside the container, so the data is cleared every time the container gets restarted. To save your data, you need to set up persistent storage (or bind mounts) for your container.

Run Prometheus container with persistent storage:

[code example]

### Custom image

To avoid managing a file on the host and bind-mount it, the
configuration can be baked into the image. This works well if the
configuration itself is rather static and the same across all
environments.

For this, create a new directory with a Prometheus configuration and a
 Dockerfile like this:

[code example]

Now build and run it:

[code example]

A more advanced option is to render the configuration dynamically on start
with some tooling or even have a daemon update it periodically.

## Using configuration management systems

If you prefer using configuration management systems you might be interested in
the following third-party contributions:

### Ansible

* prometheus-community/ansible

### Chef

* rayrod2030/chef-prometheus

### Puppet

* puppet/prometheus

### SaltStack

* saltstack-formulas/prometheus-formula