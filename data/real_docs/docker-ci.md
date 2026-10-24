Using Docker Build Cloud in CI can speed up your build pipelines, which means less time
spent waiting and context switching. You control your CI workflows as usual,
and delegate the build execution to Docker Build Cloud.

Building with Docker Build Cloud in CI involves the following steps:

1. Sign in to a Docker account.
2. Set up Buildx and connect to the builder.
3. Run the build.

When using Docker Build Cloud in CI, it's recommended that you push the result to a
registry directly, rather than loading the image and then pushing it. Pushing
directly speeds up your builds and avoids unnecessary file transfers.

If you just want to build and discard the output, export the results to the
build cache or build without tagging the image. With no explicit output, Buildx
leaves an untagged result in the cloud build cache and automatically loads
eligible tagged images. See
Loading build results for details.

> [!NOTE]
>
> Builds on Docker Build Cloud have a timeout limit that depends on your
> subscription plan. Builds that run for longer than your limit are
> automatically cancelled.

## Setting up credentials for CI/CD

To enable your CI/CD system to build and push images using Docker Build Cloud, provide both an access token and a username. The type of token and the username you use depend on your account type and permissions.

- If you are an organization administrator or have permission to create organization access tokens (OAT), use an OAT and set DOCKER_ACCOUNT to your Docker Hub organization name.
- If you do not have permission to create OATs or are using a personal account, use a personal access token (PAT) and set DOCKER_ACCOUNT to your Docker Hub username.

### Creating access tokens

#### For organization accounts

If you are an organization administrator:

- Create an organization access token (OAT). The token must have these permissions:
 1. cloud-connect scope
 2. Read public repositories permission
 3. Repository access with Image push permission for the target repository:
 - Expand the Repository drop-down.
 - Select Add repository and choose your target repository.
 - Set the Image push permission for the repository.

If you are not an organization administrator:

- Ask your organization administrator for an access token with the permissions listed above, or use a personal access token.

#### For personal accounts

- Create a personal access token (PAT) with the following permissions:
 1. Read & write access.
 - Note: Building with Docker Build Cloud only requires read access, but you need write access to push images to a Docker Hub repository.

## CI platform examples

> [!IMPORTANT]
>
> These examples require Buildx version 0.37.0 or later, which includes the
> cloud driver. The Docker CLI version doesn't determine the installed Buildx
> plugin version, and CI runner images may include an earlier Buildx release.
>
> Check the installed version:
>
> [code example]
>
> If the version is earlier than 0.37.0, install Buildx as a
> Docker CLI plugin.

> [!NOTE]
>
> In your CI/CD configuration, set the following variables/secrets:
> - DOCKER_ACCESS_TOKEN — your access token (PAT or OAT). Use a secret to store the token.
> - DOCKER_ACCOUNT — your Docker Hub organization name (for OAT) or username (for PAT)
> - CLOUD_BUILDER_NAME — the name of the cloud builder you created in the Docker Build Cloud Dashboard
>
> This ensures your builds authenticate correctly with Docker Build Cloud.

### GitHub Actions

[code example]

The example above uses docker/build-push-action , which automatically uses the
builder set up by setup-buildx-action . If you need to use the docker build 
command directly instead, you have two options:

- Use docker buildx build instead of docker build 
- Set the BUILDX_BUILDER environment variable to use the cloud builder:

 [code example]

For more information about the BUILDX_BUILDER environment variable, see
Build variables.

### GitLab

[code example]

### Circle CI

[code example]

### Buildkite

The following example sets up a Buildkite pipeline using Docker Build Cloud. The
example assumes that the pipeline name is build-push-docker and that you
manage the Docker access token using environment hooks, but feel free to adapt
this to your needs.

Add the following environment hook agent's hook directory:

[code example]

Create a pipeline.yml that uses the docker-login plugin:

[code example]

Create the build.sh script:

[code example]

### Jenkins

[code example]

### Travis CI

[code example]

### BitBucket Pipelines 

[code example]

### Shell script

[code example]

### Docker Compose

This example requires Buildx version 0.37.0 or later. Set the cloud builder as
the default builder before running docker compose build in CI:

[code example]