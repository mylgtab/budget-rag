Before you can start using Docker Build Cloud, you must add the builder to your local
environment.

## Prerequisites

To get started with Docker Build Cloud, you need to:

- Install Docker Desktop version 4.26.0 or later, or Buildx version 0.37.0 or
 later.
- Create a cloud builder on the Docker Build Cloud Dashboard.
 - When you create the builder, choose a name for it (for example, default ). You will use this name as BUILDER_NAME in the CLI steps below.

### Use Docker Build Cloud without Docker Desktop

Buildx version 0.37.0 or later includes the
 cloud driver. To use Docker Build
Cloud without Docker Desktop, check your installed version:

[code example]

If your Docker CLI installation doesn't include a compatible Buildx version,
install Buildx as a Docker
CLI plugin.

## Steps

You can add a cloud builder using the CLI, with the docker buildx create 
command, or using the Docker Desktop settings GUI.

1. Sign in to your Docker account.

 [code example]

2. Connect Buildx to your cloud builder.

 [code example]

 Replace with the Docker Hub namespace of your Docker organization (or your username if you are using a personal account), and with the name you chose when creating the builder in the dashboard.

 This registers a local endpoint for the cloud builder named cloud-ORG-BUILDER_NAME .

 > [!NOTE]
 >
 > This command connects Buildx to an existing Docker Build Cloud builder. It
 > does not create a new cloud builder. To add a new builder, use the
 > Docker Build Cloud Dashboard.

 > [!NOTE]
 >
 > If your organization is acme and you named your builder default , use:
 >
 > [code example]

1. Sign in to your Docker account using the Sign in button in Docker Desktop.

2. Open the Docker Desktop settings and navigate to the Builders tab.

3. Under Available builders , select Connect to builder .

The builder has native support for the linux/amd64 and linux/arm64 
architectures. This gives you a high-performance build cluster for building
multi-platform images natively.

## Firewall configuration

To use Docker Build Cloud behind a firewall, ensure that your firewall allows
traffic to the following addresses:

- 3.211.38.21
- https://auth.docker.io
- https://build-cloud.docker.com
- https://hub.docker.com

## What's next

- See Building with Docker Build Cloud for examples on how to use Docker Build Cloud.
- See Use Docker Build Cloud in CI for examples on how to use Docker Build Cloud with CI systems.