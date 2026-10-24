Multi-stage builds are useful to anyone who has struggled to optimize
Dockerfiles while keeping them easy to read and maintain.

## Use multi-stage builds

With multi-stage builds, you use multiple FROM statements in your Dockerfile.
Each FROM instruction can use a different base, and each of them begins a new
stage of the build. You can selectively copy artifacts from one stage to
another, leaving behind everything you don't want in the final image.

The following Dockerfile has two separate stages: one for building a binary,
and another where the binary gets copied from the first stage into the next stage.

[code example]dockerfile
# syntax=docker/dockerfile:1
FROM golang: AS build
WORKDIR /src
COPY [internal] load build definition from Dockerfile 0.0s
 => => transferring dockerfile: 36B 0.0s
 => [internal] load .dockerignore 0.0s
 => => transferring context: 2B 0.0s
 => [internal] load metadata for docker.io/library/ubuntu:latest 0.0s
 => CACHED [base 1/2] FROM docker.io/library/ubuntu 0.0s
 => [base 2/2] RUN echo "base" 0.1s
 => [stage2 1/1] RUN echo "stage2" 0.2s
 => exporting to image 0.0s
 => => exporting layers 0.0s
 => => writing image sha256:f55003b607cef37614f607f0728e6fd4d113a4bf7ef12210da338c716f2cfd15 0.0s
[code example]console
$ DOCKER_BUILDKIT=0 docker build --no-cache -f Dockerfile --target stage2 .
Sending build context to Docker daemon 219.1kB
Step 1/6 : FROM ubuntu AS base
 ---> a7870fd478f4
Step 2/6 : RUN echo "base"
 ---> Running in e850d0e42eca
base
Removing intermediate container e850d0e42eca
 ---> d9f69f23cac8
Step 3/6 : FROM base AS stage1
 ---> d9f69f23cac8
Step 4/6 : RUN echo "stage1"
 ---> Running in 758ba6c1a9a3
stage1
Removing intermediate container 758ba6c1a9a3
 ---> 396baa55b8c3
Step 5/6 : FROM base AS stage2
 ---> d9f69f23cac8
Step 6/6 : RUN echo "stage2"
 ---> Running in bbc025b93175
stage2
Removing intermediate container bbc025b93175
 ---> 09fc3770a9c4
Successfully built 09fc3770a9c4
 

The legacy builder processes stage1 , even if stage2 doesn't depend on it.