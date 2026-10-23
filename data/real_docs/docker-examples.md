This page provides complete, working policy examples you can copy and adapt.
The examples are organized into two sections: getting started policies for
quick adoption, and production templates for comprehensive security.

If you're new to policies, start with the tutorials:
Introduction, Image validation, and Git
validation. Those pages teach individual techniques. This
page shows complete policies combining those techniques.

## How to use these examples

1. Copy the policy code into a Dockerfile.rego file next to your
 Dockerfile
2. Customize any todo comments with your specific values
3. Test by running docker build. and verifying the policy works as
 expected
4. Refine based on your team's needs

### Using examples with bake

These policies work with both docker buildx build and docker buildx bake.
For bake, place the policy alongside your Dockerfile and it loads
automatically. To use additional policies:

[code example]

See the Usage guide for complete bake integration details.

## Getting started

These policies work immediately with minimal or no customization. Use them to
adopt policies quickly and demonstrate value to your team.

### Development-friendly baseline

A permissive policy that allows typical development workflows while blocking
obvious security issues.

[code example]

This policy allows local and Git contexts, images from Docker Hub, GitHub
Container Registry, and Docker Hardened Images, and ADD downloads
over HTTPS. It blocks HTTP downloads and non-standard registries.

When to use: Starting point for teams new to policies. Provides basic security
without disrupting development workflows.

### Registry allowlist

Control which registries your builds can pull images from.

[code example]

This policy restricts image pulls to approved registries. Customize and add
your internal registry to the list. If you have a DHI Enterprise subscription
and have mirrored Docker Hardened Images to Docker Hub, add a rule to allow
images from your organization's namespace.

When to use: Enforce corporate policies about approved image sources. Prevents
developers from using arbitrary public registries.

### Pin base images to digests

Require digest references for reproducible builds.

[code example]

This policy requires images use digest references like
 alpine@sha256:abc123... instead of tags like alpine:3.19. Digests are
immutable - the same digest always resolves to the same image content.

When to use: Ensure build reproducibility. Prevents builds from breaking when
upstream tags are updated. Required for compliance in some environments.

### Control external dependencies

Pin specific versions of dependencies downloaded during builds.

[code example]

This policy creates allowlists for external dependencies. Add your Git
repositories with approved version tags, and URLs.

When to use: Control which external dependencies can be used in builds.
Prevents builds from pulling arbitrary versions or unverified downloads.

## Production templates

These templates demonstrate comprehensive security patterns. They require
customization but show best practices for production environments.

### Image attestation and provenance

Require images have provenance attestations from trusted builders.

[code example]

This template validates that your application images have provenance
attestations, and were built by GitHub Actions from your main branch. Docker
Hardened Images are allowed when using digests since they include comprehensive
attestations by default. Other base images must use digests.

Customize:

- Replace allowed_repos with your image names
- Update the organization name in trusted_github_builder() 
- Add rules for other base images you use

When to use: Enforce supply chain security for production deployments. Ensures
images are built by trusted CI/CD pipelines with auditable provenance.

### Signed Git releases

Enforce signed tags from trusted maintainers for Git dependencies.

[code example]

This template requires production release tags to be signed by trusted
maintainers. Development branches and commits can be unsigned.

Setup:

1. Export maintainer PGP public keys to maintainers.asc:
 [code example]
2. Place maintainers.asc in the same directory as your policy file

Customize:

- Replace the repository URL in is_buildkit 
- Update the maintainers in the PGP keyring file
- Adjust the version tag regex pattern if needed

When to use: Validate that production dependencies come from signed releases.
Protects against compromised releases or unauthorized updates.

### Multi-registry policy

Apply different validation rules for internal and external registries.

[code example]

This template defines a trust boundary between internal and external image
sources. Internal images require minimal validation, while external images need
digests and provenance. Docker Hardened Images from dhi.io are treated as
trusted since they include comprehensive attestations and security guarantees.

Customize:

- Set your internal registry hostname
- Add your approved Docker Hub base images
- Adjust validation requirements based on your security policies

When to use: Organizations with internal registries that need different rules
for internal and external sources. Balances security with practical workflow
needs.

### Multi-environment policy

Apply different rules based on the build target or stage. For example,

[code example]

This template uses build targets to apply different validation levels.
Production requires attestations and digests, development is permissive, and
staging uses moderate rules.

Customize:

- Update environment detection logic (target names, build args, etc.)
- Adjust validation requirements for each environment
- Add more environments as needed

When to use: Teams with separate build configurations for different deployment
stages. Allows flexibility in development while enforcing strict rules for
production.

### Complete dependency pinning

Pin all external dependencies to specific versions across all input types.

[code example]

This template pins every external dependency to exact versions with cryptographic
verification. Images use digests, Git repos use commit SHAs, and downloads use
checksums.

Customize:

- Add all your dependencies with exact versions/checksums
- Maintain this file when updating dependencies
- Consider automating updates through CI/CD

When to use: Maximum reproducibility and security. Ensures builds always use
exact versions of all dependencies. Required for high-security or regulated
environments.

### Manual signature verification

Verify image signatures by inspecting signature metadata fields.

[code example]

This policy validates that images were built by GitHub Actions using Sigstore
keyless signing.

Customize:

- Replace myorg with your GitHub organization
- Adjust workflow path restrictions
- Add additional signature field checks as needed

When to use: Enforce that images are built by CI/CD with verifiable signatures,
not manually pushed by developers.

## Next steps

- Write unit tests for your policies: Test build policies
- Review Built-in functions for signature verification and
 attestation checking
- Check the Input reference for all available fields you can
 validate
- Read the tutorials for detailed explanations:
 Introduction, Image validation, Git
 validation