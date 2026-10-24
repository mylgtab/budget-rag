Docker can provision your organization's Docker Hardened Images (DHI)
subscription in the EU region. When your subscription is in the EU region,
Docker stores your mirrored and customized images in the EU.

## How your region is set

Docker sets the region on your DHI subscription. Docker doesn't detect your
region automatically. To have your subscription provisioned in the EU region,
or to change its region, contact your Docker account representative or Docker
sales.

If you plan to use the EU region, request it before you start mirroring.
Mirrors that you create before your subscription moves to the EU region stay
in their original region.

## Check your region

1. Sign in to Docker Hub.
1. Select My Hub .
1. In the namespace drop-down, select your organization.
1. Select Hardened Images > Manage .

When your subscription is in the EU region, the subscription label shows
 Your subscription (Region EU) . When it shows only Your subscription ,
your subscription is in the default US region.

## What Docker stores in the EU

When your subscription is in the EU region, Docker stores the following in the
EU:

- The repositories that Docker creates when you mirror a DHI
 repository to your organization on Docker Hub, and
 their attestations
- Your customized images and their attestations

OCI artifacts that you use in customizations are stored in the region of the
repository that you push them to. To keep them in the EU, push them to
repositories in the EU region.

Your region doesn't apply to repositories that you mirror to a third-party
registry.
Where that content is stored depends on the registry you use.

## Attestations in the EU region

Docker stores attestations with the images in your Docker Hub repository. For
mirrored repositories, Docker copies only the attestations created when the
image is built. Attestations that Docker Scout generates, such as VEX
statements and vulnerability reports, aren't available in the EU region. To
see which attestations are available, see Image
attestations.

## Limitations in the EU region

Mirroring and customization in the EU region work the same as in other regions,
with the following differences:

- You can't add files
 that you write directly in a customization, such as configuration files or
 setup scripts. This doesn't affect files that come from OCI artifacts. You can
 still add packages, OCI artifacts, and symlinks.
- Docker doesn't provide VEX statements or vulnerability reports for your
 mirrored repositories or customized images.
- Docker doesn't turn on Docker Scout image analysis for your mirrored
 repositories or customized images in the EU region. If you turn on Docker
 Scout image analysis for a repository in the EU region, the data that Docker
 Scout processes is stored in the US.