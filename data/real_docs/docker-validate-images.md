Container images are the most common build inputs. Every FROM instruction
pulls an image, and COPY --from references pull additional images. Validating
these images protects your build supply chain from compromised registries,
unexpected updates, and unauthorized base images.

This guide teaches you to write policies that validate image inputs,
progressing from basic allowlisting to advanced attestation checks.

## Prerequisites

You should understand the policy basics from the Introduction:
creating policy files, basic Rego syntax, and how policies evaluate during
builds.

## What are image inputs?

Image inputs come from two Dockerfile instructions:

[code example]

Each of these references triggers a policy evaluation. Your policy can inspect
image metadata, verify attestations, and enforce constraints before the build
proceeds.

## Allowlist specific repositories

The simplest image policy restricts which repositories can be used. This
prevents developers from using arbitrary images that haven't been vetted.

Create a policy that only allows Alpine:

[code example]

This policy:

- Denies all inputs by default
- Allows local build context
- Allows any image from the alpine repository (any tag or digest)

Test it with a Dockerfile:

[code example]

[code example]

The build succeeds. Try changing to FROM ubuntu :

[code example]

The build fails because ubuntu doesn't match the allowed repository.

## Compare semantic versions

Restrict images to specific version ranges using Rego's semver functions:

[code example]

The semver.compare(a, b) function compares semantic versions and returns:

- -1 if version a is less than b 
- 0 if versions are equal
- 1 if version a is greater than b 

Use semver.is_valid() to check if a tag is a valid semantic version before
comparing.

Restrict to specific version ranges:

[code example]

This allows only Node.js 20.x versions. The pattern works for any image using
semantic versioning.

These semver functions are standard Rego built-ins documented in the OPA
policy
reference.

## Require digest references

Tags like alpine:3.22 can change - someone could push a new image with the
same tag. Digests like alpine@sha256:abc123... are immutable.

### Requiring users to provide digests

You can require that users always specify digests in their Dockerfiles:

[code example]

The isCanonical field is true when the user's reference includes a digest.
This policy would allow:

[code example]

But reject tag-only references like FROM alpine:3.22 .

### Pinning to specific digests

Alternatively (or additionally), you can validate that an image's actual digest
matches a specific value, regardless of how the user wrote the reference:

[code example]

This checks the actual content digest of the pulled image. It would allow both:

[code example]

As long as the resolved image has the specified digest. This is useful for
pinning critical base images to known-good versions.

## Restrict registries

Control which registries your builds can pull from. This helps enforce
corporate policies or restrict to trusted sources.

[code example]

The host field contains the registry hostname. Docker Hub images use
 "docker.io" as the host value. Test with:

[code example]

Use fullRepo when you need the complete path including registry:

[code example]

## Validate platform constraints

Multi-architecture images support different operating systems and CPU
architectures. You can restrict builds to specific platforms:

[code example]

This policy:

- Defines supported architectures in a list
- Checks input.image.os matches Linux
- Verifies input.image.arch is in the supported list

The os and arch fields come from the image manifest, reflecting the actual
image platform. This works with Docker's automatic platform selection -
policies validate what Buildx resolves, not what you specify.

## Inspect image metadata

Images contain metadata like environment variables, labels, and working
directories. You can validate these to ensure images meet requirements.

Check for specific environment variables:

[code example]

This policy validates the official Go image by checking:

- The working directory is /go 
- The environment has GOLANG_VERSION set
- The environment includes GOTOOLCHAIN=local 

The input.image.env field is an array of strings in KEY=VALUE format.
Use Rego's some iteration to search the array.

Check image labels:

[code example]

The labels field is a map, so you access values with bracket notation.

## Require attestations and provenance

Modern images include attestations:
machine-readable metadata about how the image was built.
Provenance attestations
describe the build process, and SBOMs
list the software inside.

Require provenance:

[code example]

The hasProvenance field is true when the image has provenance or SBOM
attestations.

## Verify GitHub Actions signatures

For images built with GitHub Actions, verify they came from trusted workflows by
inspecting signature metadata:

[code example]

This pattern works with any GitHub Actions workflow using Sigstore keyless
signing. The signature metadata provides cryptographic proof of the build's
origin. For complete signature verification examples, see Example
policies.

## Combine multiple checks

Real policies often combine several checks. Multiple conditions in one allow 
rule means AND - all must be true:

[code example]

Multiple allow rules means OR - any rule can match:

[code example]

Use this pattern to apply different requirements to different base images.

## Next steps

You now understand how to validate container images in build policies. To
continue learning:

- Learn Git repository validation for source code inputs
- Browse Example policies for complete policy patterns
- Read Built-in functions for signature verification and
 attestation checking
- Check the Input reference for all available image fields