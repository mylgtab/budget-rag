Docker Hardened Images (DHIs) are designed to be secure by default, but like any
container image, it's important to scan them regularly as part of your
vulnerability management process.

## Scan with OpenVEX-compliant scanners

To get accurate vulnerability assessments, use scanners that support
VEX attestations. The following scanners can
read and apply the VEX statements included with Docker Hardened Images:

- Docker Scout: Automatically applies VEX statements with zero configuration
- Trivy: Supports VEX through VEX Hub or local VEX files
- Grype: Supports VEX via the --vex flag

For a full list of supported scanners, see Scanner integrations.

## Docker Scout

Docker Scout is integrated into Docker Desktop and the Docker CLI. It provides
vulnerability insights, CVE summaries, and direct links to remediation guidance.

### Scan a DHI using Docker Scout

To scan a Docker Hardened Image using Docker Scout, run the following
command:

[code example]

Example output:

[code example]

For more detailed filtering and JSON output, see Docker Scout CLI reference.

### Build child images with provenance attestations

When you build a custom image that uses a Docker Hardened Image as its base, you must build with --provenance=mode=max and --sbom=true so that Docker Scout can trace the base image lineage and correctly apply VEX statements.

Without these flags, Docker Scout cannot identify the DHI base image in
the provenance chain. As a result, it reports CVEs that are already suppressed
by VEX statements in the base image, producing false CVE positives in your
scan results.

> [!NOTE]
> Why provenance attestation is required 
>
> Docker Scout uses max-mode provenance attestations to identify the DHI base image
> and track its lineage. A cryptographically signed provenance attestation ensures that
> base image lineage is verified and tamper-resistant, giving Docker Scout the trust
> anchor it needs to correctly apply VEX statements from the base image.

To build with maximum provenance and SBOM attestations:

[code example]

After building with these flags, Docker Scout reads the full provenance
chain, matches the DHI base image, and applies its VEX statements. Scans of
your child image then reflect the correct suppressed CVEs, giving you an
accurate vulnerability assessment.

### VEX attestations in child images

If you introduce new layers in your child image and want to suppress CVEs in those layers, you can attach your own VEX attestation to the child image independently, you do not need to duplicate or aggregate the VEX statements from the DHI base image.

When docker scout cves runs against your child image, Scout reads VEX attestations from the full provenance chain and applies them cumulatively:

- Base image VEX - attached to the DHI, applied to CVEs in base image layers
- Child image VEX - attached to your image, applied to CVEs in layers you introduced

For example, if you add a requests layer to a DHI Python base image and attach a VEX statement suppressing CVE-2024-47081, Scout applies both VEX attestations independently and attributes each to its respective author:

[code example]

Scout suppresses CVEs from the DHI base VEX and CVEs from your child VEX in the same scan - no aggregate VEX document is required.

To create and attach a VEX attestation to your child image:

[code example]

> [!NOTE]
> This is only possible because you built with --provenance=mode=max. Without the full
> provenance chain, Scout cannot traverse back to the base image to retrieve its VEX attestations.

### Automate DHI scanning in CI/CD with Docker Scout

Integrating Docker Scout into your CI/CD pipeline enables you to automatically
verify that images built from Docker Hardened Images remain free from known
vulnerabilities during the build process. This proactive approach ensures the
continued security integrity of your images throughout the development
lifecycle.

#### Example GitHub Actions workflow

The following is a sample GitHub Actions workflow that builds an image, scans it and pushes to the registry only if the scan passes:

[code example]

The exit-code: true parameter ensures that the workflow fails if any critical or
high-severity vulnerabilities are detected, preventing the deployment of
insecure images.

> [!NOTE]
>
> The --provenance=mode=max and --sbom=true flags are required so that
> Docker Scout can trace the DHI base image lineage and correctly apply its
> VEX statements. Enabling the containerd image store via
> docker/setup-docker-action allows BuildKit to store attestations locally
> without pushing to a registry first. Without the containerd image store,
> Docker Engine rejects the build with: Attestation is not supported for the docker driver. 
> Switch to a different driver, or turn on the containerd image store, and try again. 
> The Push image step runs only if the scan passes, using if: success() 
> to ensure images are only pushed to the registry when they are free of
> critical or high-severity vulnerabilities.

For more details on using Docker Scout in CI, see Integrating Docker
Scout with other systems.

## Grype

Grype is an open-source scanner that checks
container images against vulnerability databases like the NVD and distro
advisories.

### Scan a DHI using Grype

To scan a Docker Hardened Image using Grype with VEX filtering, first export
the VEX attestation and then scan with the --vex flag:

[code example]

The --vex flag applies VEX statements during the scan, filtering out known
non-exploitable CVEs for accurate results.

For more information on exporting VEX attestations, see Export VEX
attestations.

## Trivy

Trivy is an open-source vulnerability
scanner for containers and other artifacts. It detects vulnerabilities in OS
packages and application dependencies.

### Scan a DHI using Trivy

After installing Trivy, you can scan a Docker Hardened Image by pulling
the image and running the scan command:

[code example]

To filter vulnerabilities using VEX statements, Trivy supports multiple
approaches. Docker recommends using VEX Hub, which provides a seamless workflow
for automatically downloading and applying VEX statements from configured
repositories.

#### Using VEX Hub (recommended)

Configure Trivy to download the Docker Hardened Images advisories repository
from VEX Hub. Run the following commands to set up the VEX repository:

[code example]

After setting up VEX Hub, you can scan a Docker Hardened Image with VEX filtering:

[code example]

For example, scanning the dhi.io/python:3.13 image:

[code example]

Example output:

[code example]

The --vex repo flag applies VEX statements from the configured repository during the scan,
which filters out known non-exploitable CVEs.

#### Using local VEX files

In addition to VEX Hub, Trivy also supports the use of local VEX files for
vulnerability filtering. You can download the VEX attestation that Docker
Hardened Images provide and use it directly with Trivy.

First, download the VEX attestation for your image:

[code example]

Then scan the image with the local VEX file:

[code example]

## Export VEX attestations

For scanners that need local VEX files (like Grype or Trivy with local files),
you can export the VEX attestations from Docker Hardened Images.

> [!NOTE]
>
> By default, VEX attestations are fetched from registry.scout.docker.com. Ensure that you can access this registry
> if your network has outbound restrictions. You can also mirror the attestations to an alternate registry. For more
> details, see Mirror to a third-party registry.

Export VEX attestations to a JSON file:

[code example]

> [!NOTE]
>
> The docker scout vex get command requires Docker Scout
> CLI version 1.18.3 or later.
>
> If the image exists locally on your device, you must prefix the image name with registry://. For example, use
> registry://docs/dhi-python:3.13 instead of docs/dhi-python:3.13.

## Explore the VEX file

After exporting the VEX attestation, you can inspect its contents to
understand what each statement means and filter by status. For a guided
walkthrough of the VEX document structure, status values, and jq filtering
commands, see Explore VEX statements in Docker Hardened
Images.