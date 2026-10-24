## Explanation

When a container starts, it uses the files and configuration provided by the image. Each container is able to create, modify, and delete files and does so without affecting any other containers. When the container is deleted, these file changes are also deleted.

While this ephemeral nature of containers is great, it poses a challenge when you want to persist the data. For example, if you restart a database container, you might not want to start with an empty database. So, how do you persist files?

### Container volumes

Volumes are a storage mechanism that provide the ability to persist data beyond the lifecycle of an individual container. Think of it like providing a shortcut or symlink from inside the container to outside the container. 

As an example, imagine you create a volume named log-data . 

[code example]

When starting a container with the following command, the volume will be mounted (or attached) into the container at /logs :

[code example]

If the volume log-data doesn't exist, Docker will automatically create it for you. 

When the container runs, all files it writes into the /logs folder will be saved in this volume, outside of the container. If you delete the container and start a new container using the same volume, the files will still be there.

> Sharing files using volumes 
>
> You can attach the same volume to multiple containers to share files between containers. This might be helpful in scenarios such as log aggregation, data pipelines, or other event-driven applications.

### Managing volumes

Volumes have their own lifecycle beyond that of containers and can grow quite large depending on the type of data and applications you’re using. The following commands will be helpful to manage volumes:

- docker volume ls - list all volumes
- docker volume rm - remove a volume (only works when the volume is not attached to any containers)
- docker volume prune - remove all unused (unattached) volumes

## Try it out

In this guide, you'll practice creating and using volumes to persist data created by a Postgres container. When the database runs, it stores files into the /var/lib/postgresql directory. By attaching the volume here, you will be able to restart the container multiple times while keeping the data.

### Use volumes

1. Download and install Docker Desktop.

2. Start a container using the Postgres image with the following command:

 [code example]

 This will start the database in the background, configure it with a password, and attach a volume to the directory PostgreSQL will persist the database files.

3. Connect to the database by using the following command:

 [code example]

4. In the PostgreSQL command line, run the following to create a database table and insert two records:

 [code example]

5. Verify the data is in the database by running the following in the PostgreSQL command line:

 [code example]

 You should get output that looks like the following:

 [code example]

6. Exit out of the PostgreSQL shell by running the following command:

 [code example]

7. Stop and remove the database container. Remember that, even though the container has been deleted, the data is persisted in the postgres_data volume.

 [code example]

8. Start a new container by running the following command, attaching the same volume with the persisted data:

 [code example]

 You might have noticed that the POSTGRES_PASSWORD environment variable has been omitted. That’s because that variable is only used when bootstrapping a new database.

9. Verify the database still has the records by running the following command:

 [code example]

### View volume contents

The Docker Desktop Dashboard provides the ability to view the contents of any volume, as well as the ability to export, import, empty, delete and clone volumes.

1. Open the Docker Desktop Dashboard and navigate to the Volumes view. In this view, you should see the postgres_data volume.

2. Select the postgres_data volume’s name.

3. The Stored Data tab shows the contents of the volume and provides the ability to navigate the files. The Container in-use tab displays the name of the container using the volume, the image name, the port number used by the container, and the target. A target is a path inside a container that gives access to the files in the volume. The Exports tab lets you export the volume. Double-clicking on a file will let you see the contents and make changes.

4. Right-click on any file to save it or delete it.

### Remove volumes

Before removing a volume, it must not be attached to any containers. If you haven’t removed the previous container, do so with the following command (the -f will stop the container first and then remove it):

[code example]

There are a few methods to remove volumes, including the following:

- Select the Delete Volume option on a volume in the Docker Desktop Dashboard.
- Use the docker volume rm command:

 [code example]
- Use the docker volume prune command to remove all unused volumes:

 [code example]

## Additional resources

The following resources will help you learn more about volumes:

- Manage data in Docker
- Volumes
- Volume mounts

## Next steps

Now that you have learned about persisting container data, it’s time to learn about sharing local files with containers.