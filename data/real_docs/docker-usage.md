Build policies validate build inputs and can check HTTP(S) requests during build
steps. This guide covers how to develop policies iteratively and apply them to
builds with docker buildx build and docker buildx bake.

## Prerequisites

- Buildx 0.31.0 or later - Check your version: docker buildx version 
- BuildKit 0.26.0 or later - Verify with: docker buildx inspect
 --bootstrap 

If you're using Docker Desktop, ensure you're on a version that includes these
updates.

## Policy development workflow

Buildx automatically loads policies that match your Dockerfile name. When you
build with Dockerfile, Buildx looks for Dockerfile.rego in the same
directory. For a file named app.Dockerfile, it looks for
 app.Dockerfile.rego. See the Advanced: Policy configuration
section for configuration options and manual policy loading.

Writing policies is an iterative process:

1. Start with a basic deny-all policy.
2. Build with debug logging to see what inputs your Dockerfile uses.
3. Add rules to allow specific sources based on the debug output.
4. Test and refine.

### Viewing inputs from your Dockerfile

To see the inputs that your Dockerfile references (images, Git repos, HTTP
downloads), build with debug logging:

[code example]

Example output for an image source:

[code example]

This shows the complete input structure, which fields are unresolved, and the
policy decision for each source. See Input reference for all
available fields.

### Testing policies with policy eval

Use docker buildx policy eval to
test whether your policy allows a specific source without running a full build.

Note: docker buildx policy eval tests the source specified as the argument.
It doesn't parse your Dockerfile to evaluate all inputs - for that, build with
--progress=plain.

Test if your policy allows the local context:

[code example]

No output means the policy allowed the source. If denied, you see:

[code example]

Test other sources:

[code example]

By default, --print shows reference information parsed from the source string
(like repo, tag, host ) without fetching from registries. To inspect
metadata that requires fetching the source (like labels, checksum, or
 hasProvenance ), specify which fields to fetch with --fields:

[code example]

Multiple fields can be specified as a comma-separated list.

### Iterative development example

Here's a practical workflow for developing policies:

1. Start with basic deny-all policy:

 [code example]

2. Build with debug logging to see what inputs your Dockerfile uses:

 [code example]

 The output shows the denied image and its input structure:

 [code example]

3. Add a rule allowing the alpine image:

 [code example]

4. Build again to verify the policy works:

 [code example]

If it fails, see Debugging for troubleshooting guidance.

## Using policies with docker build 

Once you've developed and tested your policy, apply it to real builds.

### Basic usage

Create a policy alongside your Dockerfile:

[code example]

[code example]

Build normally:

[code example]

Buildx loads the policy automatically and validates the alpine:3.19 image
before building.

### Build with different Dockerfile names

Specify the Dockerfile with -f:

[code example]

Buildx looks for app.Dockerfile.rego in the same directory.

### Build with manual policy

Add an extra policy to the automatic one:

[code example]

Both Dockerfile.rego (automatic) and extra-checks.rego (manual) must pass.

### Build without automatic policy

Use only your specified policy:

[code example]

## Block URLs in build steps

To check HTTP(S) requests from RUN instructions, add
 "caps": {"exec.proxy": true} to the policy's decision object. This enables
BuildKit's proxy, which checks requests against your input.http rules.
By default, these rules only apply to ADD downloads.

Save this policy as Dockerfile.rego alongside your Dockerfile to allow Debian
package downloads and block requests to other hosts:

[code example]

Test it with this Dockerfile:

[code example]

[code example]

The package downloads from deb.debian.org succeed. The proxy denies the request
to example.com with HTTP 403, and curl -f fails the build. Use --no-cache 
when testing to run the steps again.

To restrict individual URLs, use input.http.url or match both input.http.host 
and input.http.path. See the HTTP input reference.

The proxy supports Linux build steps. Applications must use the injected proxy
environment variables and trust BuildKit's certificate for HTTPS. BuildKit adds
the certificate to the system trust store. Traffic that bypasses the proxy is
blocked.

### Enable the proxy for a CI builder

For a dedicated CI builder, enable the proxy for all builds with
 --buildkitd-flags '--proxy-network':

[code example]

This replaces the exec.proxy opt-in in each policy file. You still need a
policy to restrict URLs.

## Using policies with bake

Bake supports automatic policy loading just like docker buildx
build. Place Dockerfile.rego alongside your Dockerfile and run:

[code example]

### Manual policy in bake files

Specify additional policies in your docker-bake.hcl:

[code example]

The policy attribute takes a list of policy files. Bake loads these in
addition to the automatic Dockerfile.rego (if it exists).

### Multiple policies in bake

[code example]

All policies must pass for the target to build successfully.

### Different policies per target

Apply different validation rules to different targets:

[code example]

Build with the appropriate target:

[code example]

### Bake with policy options

Currently, bake doesn't support policy options (reset, strict, disabled) in the
HCL file. Use command-line flags instead:

[code example]

## Testing in CI/CD

Validate policies in continuous integration by running builds with the --policy flag. For unit testing policies before running builds, see Test build policies.

Test policies during CI builds:

[code example]

This ensures policy changes don't break builds and that new rules work as
intended. The strict=true flag fails the build if policies aren't loaded (for
example, if the BuildKit instance used by the build is too old and doesn't
support policies).

## Advanced: Policy configuration

This section covers advanced policy loading mechanisms and configuration
options.

### Automatic policy loading

Buildx automatically loads policies that match your Dockerfile name. When you
build with Dockerfile, Buildx looks for Dockerfile.rego in the same
directory. For a file named app.Dockerfile, it looks for
 app.Dockerfile.rego.

[code example]

This automatic loading means you don't need command-line flags in most cases.
Create the policy file alongside your Dockerfile and build:

[code example]

Buildx detects Dockerfile.rego and evaluates it before running the build.

> [!NOTE]
> Policy files must be in the same directory as the Dockerfile they validate.
> Buildx doesn't search parent directories or subdirectories.

### When policies don't load

If Buildx can't find a matching.rego file, the build proceeds without policy
evaluation. To require policies and fail if none are found, use strict mode:

[code example]

This fails the build if no policy loads or if the BuildKit daemon doesn't
support policies.

### Manual policy configuration

The --policy flag lets you specify additional policies, override automatic
loading, or control policy behavior.

Basic syntax:

[code example]

This loads custom.rego in addition to the automatic Dockerfile.rego (if it
exists).

Multiple policies:

[code example]

All policies must pass for the build to succeed. Use this to enforce layered
requirements (base policy + project-specific rules).

Available options:

| Option | Description | Example |

| filename= | Load policy from specified file | filename=custom.rego |
| reset=true | Ignore automatic policies, use only specified ones | reset=true |
| disabled=true | Disable all policy evaluation | disabled=true |
| strict=true | Fail if BuildKit doesn't support policies | strict=true |
| log-level= | Control policy logging (error, warn, info, debug, none). Use debug to see complete input JSON and unresolved fields | log-level=debug |

Combine options with commas:

[code example]

### Exploring sources with policy eval

The docker buildx policy eval command lets you quickly explore and test
sources without running a build.

#### Inspect input structure with --print

Use --print to see the input structure for any source without running policy
evaluation:

[code example]

[code example]

Test different source types:

[code example]

Shows information parsed from the source without fetching. Use --fields to
fetch specific metadata (see above).

#### Test with specific policy files

The --filename flag specifies which policy file to load by providing the base
Dockerfile name (without the.rego extension). This is useful for testing
sources against policies associated with different Dockerfiles.

For example, to test a source against the policy for app.Dockerfile:

[code example]

This loads app.Dockerfile.rego and tests whether it allows the source. 
(the local directory). The flag defaults to Dockerfile if not specified.

Test different sources against your policy:

[code example]

### Reset automatic loading

To use only your specified policies and ignore automatic.rego files:

[code example]

This skips Dockerfile.rego and loads only custom.rego.

### Disable policies temporarily

Disable policy evaluation for testing or emergencies:

[code example]

The build proceeds without any policy checks. Use this carefully - you're
bypassing security controls.

## Next steps

- Write unit tests for your policies: Test build policies
- Debug policy failures: Debugging
- Browse working examples: Example policies
- Reference all input fields: Input reference