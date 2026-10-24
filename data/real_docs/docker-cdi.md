The Container Device Interface (CDI)
is a specification designed to standardize how devices (like GPUs, FPGAs, and
other hardware accelerators) are exposed to and used by containers. The aim is
to provide a more consistent and secure mechanism for using hardware devices in
containerized environments, addressing the challenges associated with
device-specific setups and configurations.

In addition to enabling the container to interact with the device node, CDI also
lets you specify additional configuration for the device, such as environment
variables, host mounts (such as shared objects), and executable hooks.

## Getting started

To get started with CDI, you need to have a compatible environment set up. This
includes having Docker v27+ installed with CDI configured
and Buildx v0.22+.

You also need to create the device specifications using JSON or YAML files
in one of the following locations:

* /etc/cdi 
* /var/run/cdi 
* /etc/buildkit/cdi 

> [!NOTE]
> Location can be changed by setting the specDirs option in the cdi section
> of the buildkitd.toml configuration file if you
> are using BuildKit directly. If you're building using the Docker Daemon with
> the docker driver, see Configure CDI devices
> documentation.

> [!NOTE]
> If you are creating a container builder on WSL, you need to ensure that
> Docker Desktop is installed and WSL 2 GPU Paravirtualization
> is enabled. Buildx v0.27+ is also required to mount the WSL libraries in the
> container.

## Building with a simple CDI specification

Let's start with a simple CDI specification that injects an environment variable
into the build environment and write it to /etc/cdi/foo.yaml :

[code example]

Inspect the default builder to verify that vendor1.com/device is detected
as a device:

[code example]

Now let's create a Dockerfile to use this device:

[code example]

Here we use the RUN --device command
and set vendor1.com/device which requests the first device available in the
specification. In this case it uses foo , which is the first device in
 /etc/cdi/foo.yaml .

> [!NOTE]
> RUN --device command is only
> featured in labs channel since
> Dockerfile frontend v1.14.0-labs
> and not yet available in stable syntax.

Now let's build this Dockerfile:

[code example]

It fails because the device vendor1.com/device=foo is not automatically
allowed by the build as shown in the buildx inspect output above:

[code example]

To allow the device, you can use the --allow flag
with the docker buildx build command:

[code example]

Or you can set the org.mobyproject.buildkit.device.autoallow annotation in
the CDI specification to automatically allow the device for all builds:

[code example]

Now running the build again with the --allow device flag:

[code example]

The build is successful and the output shows that the FOO environment variable
was injected into the build environment as specified in the CDI specification.

## Set up a container builder with GPU support

In this section, we will show you how to set up a container builder
using NVIDIA GPUs. Since Buildx v0.22, when creating a new container builder, a
GPU request is automatically added to the container builder if the host has GPU
drivers installed in the kernel. This is similar to using --gpus=all with the docker run 
command.

Now let's create a container builder named gpubuilder using Buildx:

[code example]

> [!NOTE]
> We made a specially crafted BuildKit image because the current BuildKit
> release image is based on Alpine that doesn't support NVIDIA drivers. The
> following image is based on Ubuntu and installs the NVIDIA client libraries
> and generates the CDI specification for your GPU in the container builder if
> a device is requested during a build.

Let's inspect this builder:

[code example]

We can see nvidia.com/gpu vendor is detected as a device in the builder which
means that drivers were detected.

Optionally you can check if NVIDIA GPU devices are available in the container
using nvidia-smi :

[code example]

## Building with GPU support

Let's create a simple Dockerfile that will use the GPU device:

[code example]

Now run the build using the gpubuilder builder we created earlier:

[code example]

As you might have noticed, the step #7 is preparing the nvidia.com/gpu 
device by installing client libraries and the toolkit to generate the CDI
specifications for the GPU.

The nvidia-smi -L command is then executed in the container using the GPU
device. The output shows the GPU UUID.

You can check the generated CDI specification within the container builder with
the following command:

[code example]

For the EC2 instance g4dn.xlarge 
used here, it looks like this:

[code example]

Congrats on your first build using a GPU device with BuildKit and CDI.