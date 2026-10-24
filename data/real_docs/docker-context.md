The docker build and docker buildx build commands build Docker images from
a Dockerfile and a context.

## What is a build context?

The build context is the set of files that your build can access.
The positional argument that you pass to the build command specifies the
context that you want to use for the build:

[code example]

You can pass any of the following inputs as the context for a build:

- The relative or absolute path to a local directory
- A remote URL of a Git repository, tarball, or plain-text file
- A plain-text file or tarball piped to the docker build command through standard input

### Filesystem contexts

When your build context is a local directory, a remote Git repository, or a tar
file, then that becomes the set of files that the builder can access during the
build. Build instructions such as COPY and ADD can refer to any of the
files and directories in the context.

A filesystem build context is processed recursively:

- When you specify a local directory or a tarball, all subdirectories are included
- When you specify a remote Git repository, the repository and all submodules are included

For more information about the different types of filesystem contexts that you
can use with your builds, see:

- Local files
- Git repositories
- Remote tarballs

### Text file contexts

When your build context is a plain-text file, the builder interprets the file
as a Dockerfile. With this approach, the build doesn't use a filesystem context.

For more information, see empty build context.

## Local context

To use a local build context, you can specify a relative or absolute filepath
to the docker build command. The following example shows a build command that
uses the current directory ( . ) as a build context:

[code example]

This makes files and directories in the current working directory available to
the builder. The builder loads the files it needs from the build context when
needed.

You can also use local tarballs as build context, by piping the tarball
contents to the docker build command. See Tarballs.

### Local directories

Consider the following directory structure:

[code example]

Dockerfile instructions can reference and include these files in the build if
you pass this directory as a context.

[code example]

[code example]

### Local context with Dockerfile from stdin

Use the following syntax to build an image using files on your local
filesystem, while using a Dockerfile from stdin.

[code example]

The syntax uses the -f (or --file) option to specify the Dockerfile to use, and
it uses a hyphen (-) as filename to instruct Docker to read the Dockerfile from
stdin.

The following example uses the current directory (.) as the build context, and
builds an image using a Dockerfile passed through stdin using a here-document.

[code example]bash
# ✅ The following works:
docker build github.com/docker/buildx#d4f088e689b41353d74f1a0bfcd6d7c0b213aed2
# ❌ The following doesn't work because the commit hash is truncated:
docker build github.com/docker/buildx#d4f088e
[code example]console
$ docker buildx build 'https://github.com/user/myrepo.git?branch=container&subdir=docker'
[code example]console
$ docker buildx build 'https://github.com/moby/buildkit.git?tag=v0.21.1&checksum=66735c67'
[code example]console
$ docker buildx build 'https://github.com/user/myrepo.git?tag=v0.1.0&commit=deadbeef'
...
#3 [internal] load git source https://github.com/user/myrepo.git?tag=v0.1.0-rc1&commit=deadbeef
#3 0.484 bb41e835b6c3523c7c45b248cf4b45e7f862bc42 refs/tags/v0.1.0
#3 ERROR: expected checksum to match deadbeef, got bb41e835b6c3523c7c45b248cf4b45e7f862bc42
[code example]dockerfile
# syntax=docker/dockerfile:1
FROM alpine
WORKDIR /src
RUN --mount=target=. \
 make REVISION=$(git rev-parse HEAD) build
[code example]console
$ docker build \
 --build-arg BUILDKIT_CONTEXT_KEEP_GIT_DIR=1
 https://github.com/user/myrepo.git#main
[code example]console
$ docker buildx build --ssh default git@github.com:user/private.git
[code example]console
$ GIT_AUTH_TOKEN= docker buildx build \
 --secret id=GIT_AUTH_TOKEN \
 https://github.com/user/private.git
[code example]console
$ docker build -f- 
[code example]bash
docker build -t myimage:latest -f- https://github.com/docker-library/hello-world.git [internal] load build definition from Dockerfile 0.0s
 => => transferring dockerfile: 64B 0.0s
 => [internal] load .dockerignore 0.0s
 => => transferring context: 2B 0.0s
 => [internal] load build context 0.0s
 => => transferring context: 2B 0.0s
 => ERROR [1/1] COPY main.c . 0.0s
------
 > [1/1] COPY main.c .:
------
Dockerfile:2
--------------------
 1 | FROM scratch
 2 | >>> COPY main.c .
 3 |
--------------------
ERROR: failed to solve: failed to compute cache key: failed to calculate checksum of ref 7ab2bb61-0c28-432e-abf5-a4c3440bc6b6::4lgfpdf54n5uqxnv9v6ymg7ih: "/main.c": not found
[code example]text
# .dockerignore
node_modules
bar
[code example]text
.
├── index.ts
├── src/
├── docker
│   ├── build.Dockerfile
│   ├── build.Dockerfile.dockerignore
│   ├── lint.Dockerfile
│   ├── lint.Dockerfile.dockerignore
│   ├── test.Dockerfile
│   └── test.Dockerfile.dockerignore
├── package.json
└── package-lock.json
[code example]gitignore
#/this/is/a/comment
[code example]text
# comment
*/temp*
*/*/temp*
temp?
[code example]text
*.md
!README.md
[code example]text
*.md
!README*.md
README-secret.md
[code example]text
*.md
README-secret.md
!README*.md
[code example]console
$ docker build --build-context docs=./docs .
[code example]dockerfile
# syntax=docker/dockerfile:1
FROM buildbase
WORKDIR /app

# Copy all files from the default context into /app/src in the build container
COPY . /app/src
RUN make bin

# Mount the files from the named "docs" context to build the documentation
RUN --mount=from=docs,target=/app/docs \
 make manpages
[code example]console
$ docker build --build-context scripts=https://github.com/user/deployment-scripts.git .
[code example]dockerfile
# syntax=docker/dockerfile:1
FROM alpine:latest

# Copy application code from the main context
COPY . /opt/app

# Run deployment scripts using the remote "scripts" context
RUN --mount=from=scripts,target=/scripts /scripts/main.sh
[code example]console
$ docker build --build-context config=./configs/prod .
[code example]dockerfile
# syntax=docker/dockerfile:1
FROM nginx:alpine

# Use the "config" context for environment-specific configurations
COPY --from=config nginx.conf /etc/nginx/nginx.conf
[code example]dockerfile
FROM alpine:
[code example]console
docker buildx build --build-context alpine:=docker-image://alpine:edge .
[code example]hcl {title=docker-bake.hcl}
target "app" {
 contexts = {
 docs = "./docs"
 }
}
[code example]console
$ docker build --build-context docs=./docs .
[code example]dockerfile {title=app.Dockerfile}
FROM mybaseimage
[code example]hcl {title=docker-bake.hcl}
target "base" {
 dockerfile = "base.Dockerfile"
}

target "app" {
 dockerfile = "app.Dockerfile"
 contexts = {
 # the target: prefix indicates that 'base' is a Bake target
 mybaseimage = "target:base"
 }
}
[code example]console
$ docker buildx bake app
 

### Further reading

For more information about working with named contexts, see:

- --build-context CLI reference
- Using Bake with additional contexts