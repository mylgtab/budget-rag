This page contains release notes for Docker Desktop for Windows 3.x. 

## Docker Desktop 3.6.0
2021-08-11

### New

- Dev Environments : You can now create a Dev Environment from your local Git repository. 
- Volume Management : You can now sort volumes by the name, the date created, and the size of the volume. You can also search for specific volumes using the Search field. For more information, see Explore volumes.

### Upgrades

- Compose V2 RC1
 - Docker compose command line completion.
 - Allow setting 0 scale/replicas.
 - Detect new container on logs —follow.
- Go 1.16.7
- Docker Engine 20.10.8
- containerd v1.4.9
- runc v1.0.1
- Kubernetes 1.21.3
- Linux kernel 5.10.47

### Bug fixes and minor changes

- Update kernel configuration to fix a performance regression in Docker Desktop 3.0.0
 that caused publishing container ports to take 10 times longer than on older
 versions. For more information, see linuxkit/linuxkit#3701
 and docker/for-mac#5668.
- Fixed a bug where the DNS server would fail after receiving an unexpectedly large datagram.
- Fixed spurious traces on iptables updates.
- Fixed slowness when adding multiple ports forwarding option.
- Fixed bug where the WSL 2 synchronization code creates dangling symlinks if the WSL 2 home directory if it is the same as the Windows home directory. Fixes docker/for-win#11668.
- Fixed docker context ls after upgrade from 3.5.x when the Linux WSL 2 home directory is the same as the Windows home directory.
- Fixed the permissions on %PROGRAMDATA%\Docker to avoid a potential Windows containers compromise. See CVE-2021-37841. Thanks to Alessio Dalla Piazza for discovering the issue and to @kevpar for helpful discussion.
- Fixed bug where the Linux home directory under WSL 2 was set to the Windows home directory e.g. /mnt/c/Users/... .
- Fixed bug where Desktop would fail to start if it could not parse CLI contexts. Fixes docker/for-win#11601.
- Fixed an issue related to log display inside a container docker/for-win#11251.
- Fixed failures of the Windows Background Intelligent Transfer Service preventing Docker Desktop to start. docker/for-win#11273

## Docker Desktop 3.5.2
2021-07-08

### New

 Dev Environments Preview : Dev Environments enable you to seamlessly collaborate with your team members without moving between Git branches to get your code onto your team members' machines. When using Dev Environments, you can share your in-progress work with your team members in just one click, and without having to deal with any merge conflicts. 

### Upgrades

- Compose V2 beta 6
 - compose run and compose exec commands use separate streams for stdout and stderr. See docker/compose-cli#1873.
 - compose run and compose exec commands support detach keys. Fixes docker/compose-cli#1709.
 - Fixed --force and --volumes flags on compose rm command. See docker/compose-cli#1844.
 - Fixed network's IPAM configuration. Service can define a fixed IP. Fixes for docker/compose-cli#1678 and docker/compose-cli#1816

- Dev Environments
 - Support VS Code Insiders. 
 - Allow users to specify a branch when cloning a project. See dev-environments#11

### Bug fixes and minor changes

- Dev Environments: Fixed a blank screen in some create and remove scenarios. Fixes dev-environments#4
- Dev Environments: Fixed error handling when removing an environment. Fixes dev-environments#8
- Dev Environments: The Start , Stop , and Share buttons are disabled while an environment is being created or removed.
- Do not automatically switch CLI contexts on application start or when switching between Windows and Linux containers. Fixes docker/for-mac#5787 and docker/for-win#11530.
- Fixed spurious traces on iptables updates.
- Fixed a delay when adding a multiple port forwarding option.

## Docker Desktop 3.5.1
2021-06-25

### New

 Dev Environments Preview : Dev Environments enable you to seamlessly collaborate with your team members without moving between Git branches to get your code onto your team members' machines. When using Dev Environments, you can share your in-progress work with your team members in just one click, and without having to deal with any merge conflicts.

 Compose V2 beta : Docker Desktop now includes the beta version of Compose V2, which supports the docker compose command as part of the Docker CLI. While docker-compose is still supported and maintained, Compose V2 implementation relies directly on the compose-go bindings which are maintained as part of the specification. The compose command in the Docker CLI supports most of the docker-compose commands and flags. It is expected to be a drop-in replacement for docker-compose . There are a few remaining flags that have yet to be implemented, see the docker-compose compatibility list for more information about the flags that are supported in the new compose command. If you run into any problems with Compose V2, you can easily switch back to Compose v1 by either by making changes in Docker Desktop Experimental Settings, or by running the command docker-compose disable-v2 . Let us know your feedback on the new ‘compose’ command by creating an issue in the Compose-CLI GitHub repository.

### Bug fixes and minor changes

- Fixed a bug where users could not install Docker Desktop when the path to the temp folder contained dots. Fixes docker/for-win#11514
- Fixed a link to the policy that provides details on how Docker handles the uploaded diagnostics data. Fixes docker/for-mac#5741

## Docker Desktop 3.5.0
2021-06-23

### New

 Dev Environments Preview : Dev Environments enable you to seamlessly collaborate with your team members without moving between Git branches to get your code onto your team members' machines. When using Dev Environments, you can share your in-progress work with your team members in just one click, and without having to deal with any merge conflicts.

 Compose V2 beta : Docker Desktop now includes the beta version of Compose V2, which supports the docker compose command as part of the Docker CLI. While docker-compose is still supported and maintained, Compose V2 implementation relies directly on the compose-go bindings which are maintained as part of the specification. The compose command in the Docker CLI supports most of the docker-compose commands and flags. It is expected to be a drop-in replacement for docker-compose . There are a few remaining flags that have yet to be implemented, see the docker-compose compatibility list for more information about the flags that are supported in the new compose command. If you run into any problems with Compose V2, you can easily switch back to Compose v1 by either by making changes in Docker Desktop Experimental Settings, or by running the command docker-compose disable-v2 . Let us know your feedback on the new ‘compose’ command by creating an issue in the Compose-CLI GitHub repository.

### Upgrades

- Compose V2 beta
 - Fixed a bug where a container cannot be started when a file is bind-mounted into a nested mountpoint. Fixes docker/compose-cli#1795.
 - Added support for container links and external links.
 - Introduced the docker compose logs --since --until option.
 - docker compose config --profiles now lists all defined profiles.
- From Kubernetes 1.21.1 to Kubernetes 1.21.2

### Bug fixes and minor changes

- Volume Management 
 - Users can now remove a file or directory inside a volume using the Docker Dashboard.
 - The Volumes view in Docker Dashboard displays the last modified time and the size of the contents inside a volume.
 - Users can save the files and directories inside a volume from Docker Dashboard.
- Fixed an issue that caused credStore timeout errors when running the docker login command. Fixes docker/for-win#11472
- Docker Desktop now allows the WSL 2 integration agent to start even when /etc/wsl.conf is malformed.
- Fixed an issue with the Docker Compose app not being stopped or removed when started by multiple configuration files. docker/for-win#11445
- Fixed a bug where Docker Desktop fails to restart after a power failure because the Hyper-V VM restarted prematurely.
- The default docker CLI context is now desktop-linux in Linux containers mode and desktop-windows when in Windows containers mode.
- Show the Docker Desktop Feedback popup only when clicking Docker menu.

## Docker Desktop 3.4.0
2021-06-09

### New

 Volume Management : Docker Desktop users can now create and delete volumes using the Docker Dashboard and also see which volumes are being used. For more information, see Explore volumes.

 Compose V2 beta : Docker Desktop now includes the beta version of Compose V2, which supports the docker compose command as part of the Docker CLI. While docker-compose is still supported and maintained, Compose V2 implementation relies directly on the compose-go bindings which are maintained as part of the specification. The compose command in the Docker CLI supports most of the docker-compose commands and flags. It is expected to be a drop-in replacement for docker-compose . There are a few remaining flags that have yet to be implemented, see the docker-compose compatibility list for more information about the flags that are supported in the new compose command. If you run into any problems with Compose V2, you can easily switch back to Compose v1 by either by making changes in Docker Desktop Experimental Settings, or by running the command docker-compose disable-v2 . Let us know your feedback on the new ‘compose’ command by creating an issue in the Compose-CLI GitHub repository.

 Skip Docker Desktop updates : All users can now skip an update when they are prompted to install individual Docker Desktop releases. 

### Deprecation

- Docker Desktop no longer installs Notary, docker trust should be used for image signing.

### Upgrades

- Docker Engine 20.10.7
- Docker Compose 1.29.2
- Docker Hub Tool v0.4.1
- Compose CLI v1.0.16
- Kubernetes 1.21.1
- containerd v1.4.6
- runc v1.0.0-rc95
- Go 1.16.5

### Bug fixes and minor changes

- Fixed error showing stderr log in the UI. Fixes docker/for-win#11251.
- Automatically reclaim space after deleting containers by deleting volumes and removing build cache.
- Docker Compose applications with file names other than docker-compose.yml can now be removed from Docker Desktop. Fixes docker/for-win#11046
- Fixed version number missing in update dialog window.
- Fixed an issue where the diagnostics were sometimes not uploaded correctly from the Support dialog.
- Fixed DNS entries for *.docker.internal and Kubernetes cluster reset after the VM IP changes.
- Fixed a corrupted internal cache which was preventing Docker Desktop from starting. Fixes docker/for-win#8748.
- Fixed an issue where docker info sometimes took longer to respond. Fixes docker/for-win#10675

## Docker Desktop 3.3.3
2021-05-06

### Upgrades

- Snyk v1.563.0
- Docker Scan v0.8.0

### Bug fixes and minor changes

- Fixed the diagnostics failing to upload from the Troubleshoot screen.

## Docker Desktop 3.3.2
2021-05-03

### Upgrades

- Compose CLI v1.0.14
- Go 1.16.3
- Docker Compose 1.29.1
- Docker Engine 20.10.6

### Bug fixes and minor changes

- Fixed a bug where a metrics-port defined in the engine's daemon.json blocks application restart.
- Fixed a leak of ephemeral ports. Fixes docker/for-mac#5611.
- Enable buildkit garbage collection by default.
- Fixed a bug which blocked binding to port 123. Fixes docker/for-mac#5589.
- Removed the "Deploy Docker Stacks to Kubernetes by default" Kubernetes setting. The component was removed in 2.4.0.0 but we forgot to remove the setting. Fixes docker/for-mac#4966.

## Docker Desktop 3.3.1
2021-04-15

### Bug fixes and minor changes

- Docker Desktop now ensures the permissions of /dev/null and other devices are correctly set to 0666 ( rw-rw-rw- ) inside --privileged containers. Fixes docker/for-mac#5527.
- Fixed an issue that caused docker run to fail when using \\wsl.localhost path to a directory. Fixes docker/for-win#10786
- Fixed an issue that caused Docker Desktop to fail during startup when it is unable to establish a connection with Docker Hub in the backend. Fixes docker/for-win#10896
- Fixed file permission when creating a file from a delta update. Fixes docker/for-win#10881

## Docker Desktop 3.3.0
2021-04-08

### New

You can now specify when to download and install a Docker Desktop update. When an update becomes available, Docker Desktop displays an icon to indicate the availability of a newer version. You can download the update in the background whenever convenient. When the download is complete, all you need to do is to click Update and restart to install the latest update.

Developers who use Docker Desktop for professional development purposes may at times need to skip a specific update. For this reason, users with a paid Docker subscription can skip notifications for a particular update when a reminder appears.

For developers in IT managed environments, who don’t have administrative access to install updates to Docker Desktop, there is now an option in the Settings menu to opt out of notifications altogether for Docker Desktop updates if your Docker ID is part of a Team subscription.

### Upgrades

- Docker Compose 1.29.0
- Compose CLI v1.0.12
- Linux kernel 5.10.25
- Snyk v1.461.0
- Docker Hub Tool v0.3.1
- containerd v1.4.4
- runc v1.0.0-rc93

### Bug fixes and minor changes

- Fixed an issue when viewing compose applications that have been started with an explicit project name. Fixes docker/for-win#10564.
- Ensure --add-host host.docker.internal:host-gateway causes host.docker.internal resolves to the host IP, rather than the IP of the IP router. See docker/for-linux#264.
- Fixed port allocation for Windows containers. Fixes docker/for-win#10552.
- Fixed an issue where running a container with a random port on the host caused Docker Desktop dashboard to incorrectly open a browser with port 0, instead of using the allocated port.
- Fixed an issue where pulling an image from Docker Hub using the Docker Desktop dashboard was failing silently.
- Perform a filesystem check when starting the Linux VM.

## Docker Desktop 3.2.2
2021-03-15

### Bug fixes and minor changes

- Fixed an issue that stopped containers binding to port 53. Fixes docker/for-win#10601.
- Fixed an issue that 32-bit Intel binaries were emulated on Intel CPUs. Fixes docker/for-win#10594.
- Fixed an issue related to high CPU consumption and frozen UI when the network connection is lost. Fixes for-win/#10563.

## Docker Desktop 3.2.1
2021-03-05

### Upgrades

- Docker Engine 20.10.5

## Docker Desktop 3.2.0
2021-03-01

### New

- The Docker Dashboard opens automatically when you start Docker Desktop.
- The Docker Dashboard displays a tip once a week.
- BuildKit is now the default builder for all users, not just for new installations. To turn this setting off, go to Settings > Docker Engine and add the following block to the Docker daemon configuration file:
[code example]

### Upgrades

- Docker Engine 20.10.3
- Docker Compose 1.28.5
- Compose CLI v1.0.9
- Docker Hub Tool v0.3.0
- QEMU 5.0.1
- Amazon ECR Credential Helper v0.5.0
- Alpine 3.13
- Kubernetes 1.19.7
- Go 1.16

### Deprecation

- Docker Desktop cannot be installed on Windows 1709 (build 16299) anymore.
- Removed the deprecated DNS name docker.for.win.localhost . Use DNS name host.docker.internal in a container to access services that are running on the host. docker/for-win#10619

### Bug fixes and minor changes

- Fixed an issue on the container detail screen where the buttons would disappear when scrolling the logs. Fixes docker/for-win#10160
- Fixed an issue when port forwarding multiple ports with an IPv6 container network. Fixes docker/for-mac#5247
- Fixed a regression where docker load could not use an xz archive anymore. Fixes docker/for-win#10364
- Fixed an issue that caused the WSL 2 backend shutdown process to interfere with Windows shutdown. Fixes docker/for-win#5825 docker/for-win#6933 docker/for-win#6446
- Fixed creds store using desktop.exe from WSL 2. Fixes docker/compose-cli#1181
- Fixed a navigation issue in the Containers / Apps view. Fixes docker/for-win#10160
- Fixed container instance view with long container/image name. Fixes docker/for-win#10160
- Fixed an issue when binding ports on specific IPs. Note: It may now take a bit of time before the docker inspect command shows the open ports. Fixes docker/for-win#10008
- Fixed an issue where an image deleted from the Docker dashboard was still displayed on the Images view.

## Docker Desktop 3.1.0
2021-01-14

## New

- Add experimental support for GPU workloads with WSL 2 backend (requires Windows Insider developer channel).
- Docker daemon now runs within a Debian Buster based container (instead of Alpine).

### Upgrades

- Compose CLI v1.0.7

### Bug fixes and minor changes

- Fixed an issue where disabling proxy settings would not work. Fixes docker/for-win#9357.
- Fixed UI reliability issues when users create or delete a lot of objects in batches.
- Redesigned the Support UI to improve usability.

## Docker Desktop 3.0.4
2021-01-06
pgrades

- Docker Engine 20.10.2

### Bug fixes and minor changes

- Fixed an issue that could cause Docker Desktop to fail to start after upgrading to 3.0.0. Fixes docker/for-win#9755.

## Docker Desktop 3.0.0
2020-12-10

## New

- Use of three-digit version number for Docker Desktop releases.
- Docker Desktop updates are now much smaller as they will be applied using delta patches. For more information, see.
- First version of docker compose (as an alternative to the existing docker-compose ). Supports some basic commands but not the complete functionality of docker-compose yet.

 - Supports the following subcommands: up , down , logs , build , pull , push , ls , ps 
 - Supports basic volumes, bind mounts, networks, and environment variables

 Let us know your feedback by creating an issue in the compose-cli GitHub repository.
- Docker Hub Tool v0.2.0

### Upgrades

- Docker Engine 20.10.0
- Go 1.15.6
- Compose CLI v1.0.4
- Snyk v1.432.0

### Bug fixes and minor changes

- Downgraded the kernel to 4.19.121 to reduce the CPU usage of hyperkit. Fixes docker/for-mac#5044
- Fixed an unexpected EOF error when trying to start a non-existing container with -v /var/run/docker.sock: . See docker/for-mac#5025.

### Known issues

- Building an image with BuildKit from a git URL fails when using the form github.com/org/repo . To work around this issue, use the form git://github.com/org/repo .
- Some DNS addresses fail to resolve within containers based on Alpine Linux 3.13.