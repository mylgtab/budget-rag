Testcontainers is a set of open source libraries that provides easy and lightweight APIs for bootstrapping local development and test dependencies with real services wrapped in Docker containers.
Using Testcontainers, you can write tests that depend on the same services you use in production without mocks or in-memory services.

## Quickstart

### Supported languages

Testcontainers provide support for the most popular languages, and Docker sponsors the development of the following Testcontainers implementations:

- Go
- Java

The rest are community-driven and maintained by independent contributors.

### Prerequisites

Testcontainers requires a Docker-API compatible container runtime.
During development, Testcontainers is actively tested against recent versions of Docker on Linux, as well as against Docker Desktop on Mac and Windows.
These Docker environments are automatically detected and used by Testcontainers without any additional configuration being necessary.

It is possible to configure Testcontainers to work for other Docker setups, such as a remote Docker host or Docker alternatives.
However, these are not actively tested in the main development workflow, so not all Testcontainers features might be available
and additional manual configuration might be necessary.

If you have further questions about configuration details for your setup or whether it supports running Testcontainers-based tests,
contact the Testcontainers team and other users from the Testcontainers community on Slack.

## Guides

Explore hands-on Testcontainers guides to learn how to use Testcontainers
with different languages and popular frameworks:

- Getting started with Testcontainers for .NET
- Getting started with Testcontainers for Go
- Getting started with Testcontainers for Java
- Getting started with Testcontainers for Node.js
- Getting started with Testcontainers for Python
- Testing a Spring Boot REST API with Testcontainers
- Testcontainers container lifecycle management
- Replace H2 with a real database for testing
- Configuration of services running in a container
- Testing an ASP.NET Core web app