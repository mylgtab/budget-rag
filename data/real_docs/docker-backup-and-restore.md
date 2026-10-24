Use this procedure to back up and restore your images and container data. This is useful if you want to reset your VM disk or to move your Docker environment to a new computer, or recover from a failed Docker Desktop update or installation.

> [!IMPORTANT]
>
> If you use volumes or bind-mounts to store your container data, backing up your containers may not be needed, but make sure to remember the options that were used when creating the container or use a Docker Compose file if you want to re-create your containers with the same configuration after re-installation.

## If Docker Desktop is functioning normally

### Save your data

1. Commit your containers to an image with docker container commit .

 Committing a container stores filesystem changes and some container configurations, such as labels and environment variables, as a local image. Be aware that environment variables may contain sensitive
 information such as passwords or proxy-authentication, so take care when pushing the resulting image to a registry.

 Also note that filesystem changes in a volume that are attached to the
 container are not included in the image, and must be backed up separately.

 If you used a named volume to store container data, such as databases, refer to the back up, restore, or migrate data volumes page in the storage section.

1. Use docker push to push any
 images you have built locally and want to keep to the Docker Hub registry.
 
 > [!TIP]
 >
 > Set the repository visibility to private if your image includes sensitive content.

 Alternatively, use [ docker image save -o images.tar image1 [image2 ...] ](/reference/cli/docker/image/save/)
 to save any images you want to keep to a local .tar file. 

After backing up your data, you can uninstall the current version of Docker Desktop
and install a different version or reset Docker Desktop to factory defaults.

### Restore your data

1. Load your images.

 - If you pushed to Docker Hub:
 
 [code example]
 
 - If you saved a .tar file:
 
 [code example]

1. Re-create your containers if needed, using docker run ,
 or Docker Compose.

To restore volume data, refer to backup, restore, or migrate data volumes. 

## If Docker Desktop fails to start or you want to back up the whole Docker Desktop VM

If Docker Desktop cannot launch and must be reinstalled, you can back up its VM disk and image data directly from disk. Docker Desktop must be fully stopped before backing up these files.

> [!NOTE]
>
> The paths below are the default locations. If you've customized the
> Disk image location setting ( Settings > Resources > Advanced ),
> back up the file at your configured location instead.

Docker Desktop on Windows stores VM data in a different location depending on
which backend you're using. Check Settings > General > Choose
Virtual Machine Manager (VMM) to see which one applies to you.

1. Back up Docker containers/images.

 For WSL 2, back up the following file:

 [code example]

 If you're running any WSL Linux distributions (Ubuntu, Alpine, etc.), back
 them up separately using Microsoft's guide.

 For Hyper-V, back up the following file:

 [code example]

 For Docker VMM (Beta), back up the following file:

 [code example]

1. Copy your back-up to a safe location. 

1. After reinstalling Docker Desktop, restore the .vhdx file to the same location for your backend, and re-import your WSL distributions if needed.

1. Back up Docker containers/images.

 Backup the following file:

 [code example]

 Copy it to a safe location. 

 > [!TIP]
 >
 > To include Docker Desktop data in Time Machine backups, make sure the ~/Library/Containers/com.docker.docker directory is not excluded from your Time Machine backup configuration.

1. Restore. 

 After reinstalling Docker Desktop, restore the Docker.raw to the same location.

1. Back up Docker containers/images:

 Backup the following file:

 [code example]

 Copy it to a safe location.

1. Restore. 

 After reinstalling Docker Desktop, restore the Docker.raw to the same location.