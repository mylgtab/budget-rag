Docker Hardened System Packages are built from source by Docker. This ensures
supply chain integrity throughout your entire image stack by eliminating risks
from potentially compromised public packages.

Access to hardened packages varies by subscription:

- DHI Community: Includes hardened packages in base images. Can configure the
 public package repository to access the same packages in custom images.
- DHI Select: Includes all Community packages, plus access to additional
 compliance-specific packages (such as FIPS variants) and Docker-patched
 packages through the image customization UI.
- DHI Enterprise: Includes all Select packages, plus the ability to configure
 the enterprise package repository directly in your own images for full access
 to compliance and security-patched packages.

To browse the packages currently available in Docker's public hardened package
repositories, see the following indexes:

- Debian package index
- Alpine package index

Docker is constantly adding new hardened packages. If a package you need isn't
available yet, you can request it in the DHI catalog
repository.

## Built-in packages

Supported distributions of Docker Hardened Images (DHI) automatically include
hardened system packages. No additional configuration is required. Simply pull
and use the images as normal.

All packages in these images are built by Docker from source, maintaining
the same security standards as the base images themselves.

## Add hardened packages to your images

You can add hardened packages to your own images in the following two ways.

### Add packages through image customization

When customizing Docker Hardened Images with DHI Select or DHI Enterprise, you
can add hardened packages for Alpine-based images through the customization
interface. Follow the steps to create an image
customization and select hardened
packages during the customization process.

### Configure the package manager

You can configure your package manager to pull from Docker's hardened package
repositories. This lets you install hardened packages in your own images.

#### Public repository

To use Docker's public hardened package repository in your own images,
configure your package manager in your Dockerfile to install the DHI signing
key and add the DHI repository.

The configuration process involves three steps:

1. Install the signing key
2. Configure the package repository
3. Update and install packages

The following example shows how to configure the Alpine package manager in your
Dockerfile to use Docker's public hardened package repository:

[code example]

Replace 3.23 with your Alpine version in both the base image tag and repository URL.
Supported versions include Alpine 3.23 and 3.24.

To verify the configuration, build and run the image:

[code example]

Inside the container, check the configured repositories:

[code example]

This ensures all packages are installed from Docker's hardened repository.

The following example shows how to configure the Debian package manager in your
Dockerfile to use Docker's public hardened package repository:

[code example]

To verify the configuration, build and run the image:

[code example]

Inside the container, check the configured repository:

[code example]

When the DHI repository carries a hardened version of a package, apt prefers
it over the upstream Debian version automatically. You can confirm this with
 apt-cache policy, which shows a candidate with a +dhi or dhi 
version suffix sourced from https://dhi.io/deb/debian/main.

Not every Debian package is available as a hardened system package. When a
package is not in the DHI repository, apt transparently falls back to the
upstream Debian mirrors configured in the base image.

All packages installed from the Docker Hardened Images repository are built from
source by Docker and include full provenance.

#### Enterprise repository

With DHI Enterprise, you have access to an additional package
repository that includes hardened packages for compliance variants such as FIPS,
as well as additional security patches.

The configuration process involves five steps:

1. Install the signing keys
2. Configure the base package repository
3. Add the enterprise security repository
4. Configure package installation with authentication
5. Build the image passing credentials as a secret using the DHI CLI

The following example shows how to configure the Alpine package manager in your
Dockerfile to use Docker's enterprise hardened package repository:

[code example]

Build the image with authentication passed securely as a build secret:

[code example]

The --secret flag securely mounts the authentication credentials during build
without storing them in the image layers or metadata.

The following example shows how to configure the Debian package manager in your
Dockerfile to use Docker's enterprise hardened package repository. Mount
credentials at /etc/apt/auth.conf.d/dhi.conf; apt reads files in
 /etc/apt/auth.conf.d/ automatically when they have mode 0600:

[code example]

Build the image, passing credentials securely as a build secret through an
environment variable:

[code example]

The --secret id=netrc,env=NETRC form securely mounts the authentication
credentials during build without storing them in the image layers or metadata.

## Verify packages

Every hardened package is cryptographically signed and includes metadata that
proves its provenance and build integrity. You can verify the signatures and
view the metadata to ensure your packages come from Docker's trusted build
infrastructure.

### View package metadata

To view information about a hardened package:

[code example]

[code example]

This shows the files included in the package and its metadata.

### Verify package signatures

Hardened packages are cryptographically signed by Docker. When you install the
signing keys and configure your package manager as described previously, the
package manager automatically verifies signatures during installation.

If a package fails signature verification, the package manager will refuse to
install it, protecting you from tampered or compromised packages.

### Build provenance and cryptographic verification

Docker hardened packages are built by Docker's trusted infrastructure and include
verifiable metadata and cryptographic signatures.

To view this metadata for an installed package:

[code example]

[code example]

Or to view metadata for a package before installing:

[code example]

[code example]

The package signing keys ensure that packages haven't been tampered with after
being built. When you install the signing key and configure your package manager,
all packages are automatically verified before installation.

### Package attestations

Each hardened package includes its own attestations, similar to image
attestations. These attestations provide provenance and build
information for individual packages, allowing you to trace the supply chain down
to the package level.

You can retrieve package attestations by first extracting package information
from the image's SLSA provenance, then using the package digest to access its
attestations.

#### Extract package information from image attestations

To get provenance information for a specific package from an image's SLSA
provenance attestation, you first need to retrieve the image's provenance and
then filter for the specific package you're interested in.

The SLSA provenance attestation includes a materials array that lists all
build inputs, including packages. You can use jq to filter this array for a
specific package:

[code example]

Replace the package URI in the select() filter with the specific package
you're looking for. You can find available packages by first running the command
without the select() filter to see all materials.

This returns the package URI and its SHA-256 digest:

[code example]

#### List attestations for a package

Using the package digest from the previous section, you can list all available
attestations for that package:

[code example]

This returns information about the package and its available attestations:

[code example]

#### Retrieve package attestations

To retrieve the actual attestation content, use the URL provided in the
attestation list:

[code example]

This returns the full SLSA provenance attestation for the package, which
includes information about how the package was built, its dependencies, and
other build materials.

You can continue this process recursively to trace the supply chain all the way
down to the compiler and other build tools used to create the package.