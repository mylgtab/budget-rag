Subscribe to security RSS feed

## Docker Sandboxes response to eMudhra CA compromise

_Last updated October 21, 2026_

Following the eMudhra certificate authority compromise, Docker rebuilt the
sandbox template images for all built-in kits with updated CA certificates.
Refresh cached images and update existing sandboxes to receive this protection.

On October 20, 2026, researchers disclosed the compromise of private keys for
eight eMudhra intermediate certificate authorities. An attacker with these keys
could impersonate websites or services to clients that still trust the
compromised certificates. See the
incident report for details.

Updating the sbx CLI alone doesn't update existing sandboxes.

### Recreate sandboxes with updated images

Recreate each sandbox using --pull always to fetch the updated images instead
of reusing cached copies. For example, for a Codex sandbox, run these commands
on your host:

[code example]

Replace codex with your agent and restore any options you used to create the
sandbox, such as --clone or additional kits. Before removing a sandbox, save
any files you need from inside it, including unpushed commits in clone mode.
Removing a sandbox deletes its filesystem.

Use --pull always when creating additional sandboxes from built-in kits.
Pulling updated images doesn't change sandboxes that already exist.

### Update CA certificates in existing sandboxes

If you need to keep an existing sandbox, update its ca-certificates package.
For Ubuntu-based Docker templates, run these commands on your host while the
sandbox is running:

[code example]

Restart applications in the sandbox after updating. Tools that bundle their
own CA certificates may also need updates. See the incident report's
patched software versions.
For custom templates, update the trust store using the base distribution's
security updates and rebuild the images before creating more sandboxes.

## Docker Sandboxes 0.42.0 security update: CVE-2026-77179 and CVE-2026-79994

Two vulnerabilities in Docker Sandboxes were fixed on September 7 in the
0.42.0 release:

- Addressed CVE-2026-77179,
 where the virtio-fs host server on macOS followed symlinks when reopening an
 unlinked file from a stored path. A malicious guest could replace a parent
 directory with a symlink, escape the shared workspace, and read or modify
 arbitrary host files as the VMM user, potentially leading to code execution on
 the host. Versions 0.28.0 up to but not including 0.42.0 on macOS are
 affected. [Critical]
- Addressed CVE-2026-79994,
 where the guest-to-host Unix domain socket relay checked that a socket path
 was inside an authorized workspace but reconnected using the path name. A
 malicious guest could replace an intermediate directory with a symlink between
 the check and the connection, causing the host to connect to an arbitrary
 AF_UNIX socket outside the shared workspace and exposing data or host-side
 capabilities provided by that socket. Versions 0.37.0 up to but not including
 0.42.0 are affected. [High]

If you can't update to 0.42.0 or
later, use clone mode and avoid
adding read-write host mounts.

## Docker Desktop 4.86.0 security update: CVE-2026-17106

A vulnerability in Docker Desktop was fixed on August 10 in the
4.86.0 release:

- Addressed CVE-2026-17106, a destination-escape flaw in docker container cp .

## Docker Desktop 4.71.0 security update: CVE-2026-5843

A vulnerability in Docker Desktop was fixed on April 27 in the
4.71.0 release:

- Addressed CVE-2026-5843,
 container-to-host code execution in the Docker Model Runner MLX inference
 backend.

## Docker Desktop 4.68.0 security update: CVE-2026-5817

A vulnerability in Docker Desktop was fixed on April 7 in the
4.68.0 release:

- Addressed CVE-2026-5817,
 container-to-host code execution in the Docker Model Runner vllm-metal
 inference backend.

## Docker Desktop 4.67.0 security update: CVE-2026-33990

A vulnerability in Docker Desktop was fixed on March 30 in the
4.67.0 release:

- Addressed CVE-2026-33990,
 SSRF in Docker Model Runner OCI Registry Client.

## Docker Desktop 4.62.0 security update: CVE-2026-28400

A vulnerability in Docker Desktop was fixed on February 23 in the
4.62.0 release:

- Addressed CVE-2026-28400,
 runtime flag injection in Docker Model Runner.

## Docker Desktop 4.62.0 security update: CVE-2026-2664

A vulnerability in Docker Desktop was fixed on February 23 in the
4.62.0 release:

- Fixed CVE-2026-2664, out of
 bounds read in gRPC-FUSE kernel module.

## Docker Desktop 4.54.0 security update: CVE-2025-13743

A vulnerability in Docker Desktop was fixed on December 4 in the
4.54.0 release:

- Fixed CVE-2025-13743 where
 Docker Desktop diagnostics bundles were found to include expired Hub PATs in
 log output due to error object serialization.

## Docker Desktop 4.49.0 security update: CVE-2025-9164

A vulnerability in Docker Desktop for Windows was fixed on October 23 in the
4.49.0 release:

- Fixed CVE-2025-9164 where
 the Docker Desktop for Windows installer was vulnerable to DLL hijacking due
 to insecure DLL search order. The installer searches for required DLLs in the
 user's Downloads folder before checking system directories, allowing local
 privilege escalation through malicious DLL placement.

## Docker Desktop 4.47.0 security update: CVE-2025-10657

A vulnerability in Docker Desktop was fixed on September 25 in the
4.47.0 release:

- Fixed CVE-2025-10657 where
 the Enhanced Container Isolation
 Docker Socket command restrictions
 feature was not working properly in Docker Desktop 4.46.0 only (the
 configuration for it was being ignored).

## Docker Desktop 4.44.3 security update: CVE-2025-9074

_Last updated August 20, 2025_

A vulnerability in Docker Desktop was fixed on August 20 in the
4.44.3 release:

- Fixed CVE-2025-9074 where a
 malicious container running on Docker Desktop could access the Docker Engine
 and launch additional containers without requiring the Docker socket to be
 mounted. This could allow unauthorized access to user files on the host
 system. Enhanced Container Isolation (ECI) does not mitigate this
 vulnerability.

## Docker Desktop 4.44.0 security update: CVE-2025-23266

_Last updated July 31, 2025_

Docker is aware of
CVE-2025-23266, a critical
vulnerability affecting the NVIDIA Container Toolkit in CDI mode up to version
1.17.7. Docker Desktop includes version 1.17.8, which is not impacted. However,
older versions of Docker Desktop that bundled earlier toolkit versions may be
affected if CDI mode was manually enabled. Upgrade to Docker Desktop 4.44 or
later to ensure you're using the patched version.

## Docker Desktop 4.43.0 security update: CVE-2025-6587

_Last updated July 3, 2025_

A vulnerability in Docker Desktop was fixed on July 3 in the
4.43.0 release:

- Fixed CVE-2025-6587 where
 sensitive system environment variables were included in Docker Desktop
 diagnostic logs, allowing for potential secret exposure.

## Docker Desktop 4.41.0 security update: CVE-2025-3224, CVE-2025-4095, and CVE-2025-3911

_Last updated May 15, 2025_

Three vulnerabilities in Docker Desktop were fixed on April 28 in the
4.41.0 release.

- Fixed CVE-2025-3224 allowing
 an attacker with access to a user machine to perform an elevation of privilege
 when Docker Desktop updates.
- Fixed CVE-2025-4095 where
 Registry Access Management (RAM) policies were not enforced when using a MacOS
 configuration profile, allowing users to pull images from unapproved
 registries.
- Fixed CVE-2025-3911 allowing
 an attacker with read access to a user's machine to obtain sensitive
 information from Docker Desktop log files, including environment variables
 configured for running containers.

Update to Docker Desktop
4.41.0.

## Docker Desktop 4.34.2 security update: CVE-2024-8695 and CVE-2024-8696

_Last updated September 13, 2024_

Two remote code execution (RCE) vulnerabilities in Docker Desktop related to
Docker Extensions were reported by Cure53 and were fixed
on September 12 in the 4.34.2 release.

- CVE-2024-8695: A remote code
 execution (RCE) vulnerability via crafted extension description/changelog
 could be abused by a malicious extension in Docker Desktop before 4.34.2.
 [Critical]
- CVE-2024-8696: A remote code
 execution (RCE) vulnerability via crafted extension
 publisher-url/additional-urls could be abused by a malicious extension in
 Docker Desktop before 4.34.2. [High]

No existing extensions exploiting the vulnerabilities were found in the
Extensions Marketplace. The Docker Team will be closely monitoring and
diligently reviewing any requests for publishing new extensions.

Update to Docker Desktop
4.34.2. If you are unable to update
promptly, you can
disable Docker Extensions
as a workaround.

## Deprecation of password logins on CLI when SSO enforced

_Last updated July 2024_

When
SSO enforcement
was first introduced, Docker provided a grace period to continue to let
passwords be used on the Docker CLI when authenticating to Docker Hub. This was
allowed so organizations could adopt SSO enforcement. It is recommended that
administrators configuring SSO encourage users using the CLI
to switch over to Personal Access Tokens
in anticipation of this grace period ending.

On September 16, 2024, the grace period ended and passwords can no longer
authenticate to Docker Hub via the Docker CLI when SSO is enforced. Affected
users are required to switch over to using PATs to continue signing in.

This deprecation is a step toward a secure experience for developers and
organizations.

## SOC 2 Type 2 attestation and ISO 27001 certification

_Last updated June 2024_

Docker received its SOC 2 Type 2 attestation and ISO 27001 certification with
no exceptions or major non-conformities.

Security is part of Docker's operations, mission, and company strategy.
Docker's products are core to the user community, and the SOC 2 Type 2
attestation and ISO 27001 certification demonstrate Docker's ongoing commitment
to security.

For more information, see the
Blog announcement.

## Docker security advisory: multiple vulnerabilities in runc, BuildKit, and Moby

_Last updated February 2, 2024_

Docker prioritizes the security and integrity of its software and the trust of
its users. Security researchers at Snyk Labs identified and reported four
security vulnerabilities in the container ecosystem. One of the vulnerabilities,
CVE-2024-21626, concerns the runc
container runtime, and the other three affect BuildKit
(CVE-2024-23651,
CVE-2024-23652, and
CVE-2024-23653). Docker, in
collaboration with the reporters and open source maintainers, coordinated and
implemented the remediations.

Docker published patched versions of runc, BuildKit, and Moby on January 31 and
released an update for Docker Desktop on February 1 to address these
vulnerabilities. The latest BuildKit and Moby releases also included fixes for
CVE-2024-23650 and
CVE-2024-24557, discovered
respectively by an independent researcher and through Docker's internal research
initiatives.

| | Versions impacted |
| :--------------------- | :---------------------- |
| runc | = 1.1.12 |
| BuildKit | >= 0.12.5 |
| Moby (Docker Engine) | >= 25.0.2 and >= 24.0.9 |
| Docker Desktop | >= 4.27.1 |

If you are unable to update to an unaffected version promptly, follow these best
practices to mitigate risk:

- Only use trusted Docker images (such as
 Docker Official Images).
- Don't build Docker images from untrusted sources or untrusted Dockerfiles.
- If you are a Docker Business customer using Docker Desktop and unable to
 update to v4.27.1, make sure to enable
 Hardened Docker Desktop
 features such as:
 - Enhanced Container Isolation,
 which mitigates the impact of CVE-2024-21626 in the case of running
 containers from malicious images.
 - Image Access Management,
 and
 Registry Access Management,
 which give organizations control over which images and repositories their
 users can access.
- For CVE-2024-23650, CVE-2024-23651, CVE-2024-23652, and CVE-2024-23653, avoid
 using BuildKit frontend from an untrusted source. A frontend image is usually
 specified as the #syntax line on your Dockerfile, or with --frontend flag
 when using the buildctl build command.
- To mitigate CVE-2024-24557, make sure to either use BuildKit or disable
 caching when building images. From the CLI this can be done via the
 DOCKER_BUILDKIT=1 environment variable (default for Moby >= v23.0 if the
 Buildx plugin is installed) or the --no-cache flag . If you are using the
 HTTP API directly or through a client, the same can be done by setting
 nocache to true or version to 2 for the
 /build API endpoint.

### Technical details and impact

#### CVE-2024-21626 (High)

In runc v1.1.11 and earlier, due to certain leaked file descriptors, an attacker
can gain access to the host filesystem by causing a newly-spawned container
process (from runc exec ) to have a working directory in the host filesystem
namespace, or by tricking a user to run a malicious image and allow a container
process to gain access to the host filesystem through runc run . The attacks
can also be adapted to overwrite semi-arbitrary host binaries, allowing for
complete container escapes. Note that when using higher-level runtimes (such as
Docker or Kubernetes), this vulnerability can be exploited by running a
malicious container image without additional configuration or by passing
specific workdir options when starting a container. The vulnerability can also
be exploited from within Dockerfiles in the case of Docker.

_The issue has been fixed in runc v1.1.12._

#### CVE-2024-23651 (High)

In BuildKit = v25.0.2 and >= v24.0.9._

### How are Docker products affected?

#### Docker Desktop

Docker Desktop v4.27.0 and earlier are affected. Docker Desktop v4.27.1 was
released on February 1 and includes runc, BuildKit, and dockerd binaries
patches. In addition to updating to this new version, use only trusted Docker
images and Dockerfiles in your builds.

As always, you should check Docker Desktop system requirements for your
operating system
(Windows,
Linux,
Mac) before
updating to ensure full compatibility.

#### Docker Build Cloud

Any new Docker Build Cloud builder instances will be provisioned with the latest
Docker Engine and BuildKit versions and will, therefore, be unaffected by these
CVEs. Updates have also been rolled out to existing Docker Build Cloud builders.

_No other Docker products are affected by these vulnerabilities._

### Advisory links

- Runc
 - CVE-2024-21626
- BuildKit
 - CVE-2024-23650
 - CVE-2024-23651
 - CVE-2024-23652
 - CVE-2024-23653
- Moby
 - CVE-2024-24557

## Text4Shell CVE-2022-42889

_Last updated October 2022_

CVE-2022-42889 has been
discovered in the popular Apache Commons Text library. Versions of this library
up to but not including 1.10.0 are affected by this vulnerability.

Update to the latest version of
Apache Commons Text.

### Scan images on Docker Hub

Docker Hub security scans triggered after 1200 UTC 21 October 2021 are now
correctly identifying the Text4Shell CVE. Scans before this date do not
currently reflect the status of this vulnerability. Trigger scans by pushing
new images to Docker Hub to view the status of the Text4Shell CVE in the
vulnerability report. For detailed instructions, see
Scan images on Docker Hub.

### Docker Official Images impacted by CVE-2022-42889

A number of
Docker Official Images
contain the vulnerable versions of Apache Commons Text. The following lists
Docker Official Images that may contain the vulnerable versions of Apache
Commons Text:

- bonita
- Couchbase
- Geonetwork
- neo4j
- sliverpeas
- solr
- xwiki

Docker updated Apache Commons Text in these images to the latest version. Some
of these images may not be vulnerable for other reasons. Also review the
guidelines published on the upstream websites.

## Log4j 2 CVE-2021-44228

_Last updated December 2021_

The Log4j 2 CVE-2021-44228
vulnerability in Log4j 2, a common Java logging library, allows remote code
execution, often from a context that is available to an attacker. For example,
it was found in Minecraft servers which allowed the commands to be typed into
chat logs as these were then sent to the logger. This makes it a serious
vulnerability, as the logging library is used so widely and it may be simple
to exploit. Many open source maintainers are working hard with fixes and
updates to the software ecosystem.

The vulnerable versions of Log4j 2 are versions 2.0 to version 2.14.1 inclusive.
The first fixed version is 2.15.0. Update to the
latest version if you can.
If you are using a version before 2.0, you are also not vulnerable.

You may not be vulnerable if you are using these versions, as your configuration
may already mitigate this, or the things you log may not include any user input.
This may be difficult to validate however without understanding all the code
paths that may log in detail, and where they may get input from. So you probably
will want to upgrade all code using vulnerable versions.

> CVE-2021-45046
>
> As an update to
> CVE-2021-44228, the fix
> made in version 2.15.0 was incomplete. Additional issues have been identified
> and are tracked with
> CVE-2021-45046 and
> CVE-2021-45105. For a more
> complete fix to this vulnerability, update to 2.17.0 where possible.

### Scan images on Docker Hub

Docker Hub security scans triggered after 1700 UTC 13 December 2021 are now
correctly identifying the Log4j 2 CVEs. Scans before this date do not currently
reflect the status of this vulnerability. Trigger scans by pushing new images
to Docker Hub to view the status of Log4j 2 CVE in the vulnerability report.
For detailed instructions, see
Scan images on Docker Hub.

## Docker Official Images impacted by Log4j 2 CVE

_Last updated December 2021_

A number of
Docker Official Images
contain the vulnerable versions of Log4j 2 CVE-2021-44228. The following table
lists Docker Official Images that may contain the vulnerable versions of Log4j
2. Docker updated Log4j 2 in these images to the latest version. Some of these
images may not be vulnerable for other reasons. Also review the guidelines
published on the upstream websites.

| Repository | Patched version | Additional documentation |
| :------------------------------------------------------ | :----------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| couchbase | 7.0.3 | Couchbase blog |
| Elasticsearch | 6.8.22, 7.16.2 | Elasticsearch announcement |
| Flink | 1.11.6, 1.12.7, 1.13.5, 1.14.2 | Flink advice on Log4j CVE |
| Geonetwork | 3.10.10 | Geonetwork GitHub discussion |
| lightstreamer | Awaiting info | Awaiting info |
| logstash | 6.8.22, 7.16.2 | Elasticsearch announcement |
| neo4j | 4.4.2 | Neo4j announcement |
| solr | 8.11.1 | Solr security news |
| sonarqube | 8.9.5, 9.2.2 | SonarQube announcement |
| storm | Awaiting info | Awaiting info |

> [!NOTE]
>
> Although xwiki images may be detected as
> vulnerable by some scanners, the authors believe the images are not vulnerable
> by Log4j 2 CVE as the API jars do not contain the vulnerability. The
> Nuxeo image is deprecated and will not be
> updated.