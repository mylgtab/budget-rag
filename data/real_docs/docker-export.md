Did you know that you can use Docker to build your application to standalone
binaries? Sometimes, you don’t want to package and distribute your application
as a Docker image. Use Docker to build your application, and use exporters to
save the output to disk.

The default output format for docker build is a container image. That image is
automatically loaded to your local image store, where you can run a container
from that image, or push it to a registry. Under the hood, this uses the default
exporter, called the docker exporter.

To export your build results as files instead, you can use the --output flag,
or -o for short. The --output flag lets you change the output format of
your build.

## Export binaries from a build

If you specify a filepath to the docker build --output flag, Docker exports
the contents of the build container at the end of the build to the specified
location on your host's filesystem. This uses the local 
exporter.

The neat thing about this is that you can use Docker's powerful isolation and
build features to create standalone binaries. This
works well for Go, Rust, and other languages that can compile to a single
binary.

The following example creates a simple Rust program that prints "Hello,
World!", and exports the binary to the host filesystem.

1. Create a new directory for this example, and navigate to it:

 [code example]

2. Create a Dockerfile with the following contents:

 [code example]console
 $ docker build --output=. .
 [code example]dockerfile
# syntax=docker/dockerfile:1
FROM rust:alpine AS build
WORKDIR /src
COPY <<EOT hello.rs
fn main() {
 println!("Hello World!");
}
EOT
RUN rustc -o /bin/hello hello.rs

FROM scratch
COPY --from=build /bin/hello /
ENTRYPOINT ["/hello"]
[code example]console
$ docker build --platform=linux/amd64,linux/arm64 --output=out .
$ tree out/
out/
├── linux_amd64
│   └── hello
└── linux_arm64
 └── hello

3 directories, 2 files
 

## Additional information

In addition to the local exporter, there are other exporters available. To
learn more about the available exporters and how to use them, see the
exporters documentation.