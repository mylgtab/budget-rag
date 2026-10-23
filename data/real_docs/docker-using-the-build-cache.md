## Explanation

Consider the following Dockerfile that you created for the getting-started app.

[code example]

When you run the docker build command to create a new image, Docker executes each instruction in your Dockerfile, creating a layer for each command and in the order specified. For each instruction, Docker checks whether it can reuse the instruction from a previous build. If it finds that you've already executed a similar instruction before, Docker doesn't need to redo it. Instead, it’ll use the cached result. This way, your build process becomes faster and more efficient, saving you valuable time and resources.

Using the build cache effectively lets you achieve faster builds by reusing results from previous builds and skipping unnecessary work.
In order to maximize cache usage and avoid resource-intensive and time-consuming rebuilds, it's important to understand how cache invalidation works.
Here are a few examples of situations that can cause cache to be invalidated:

- Any changes to the command of a RUN instruction invalidates that layer. Docker detects the change and invalidates the build cache if there's any modification to a RUN command in your Dockerfile.

- Any changes to files copied into the image with the COPY or ADD instructions. Docker keeps an eye on any alterations to files within your project directory. Whether it's a change in content or properties like permissions, Docker considers these modifications as triggers to invalidate the cache.

- Once one layer is invalidated, all following layers are also invalidated. If any previous layer, including the base image or intermediary layers, has been invalidated due to changes, Docker ensures that subsequent layers relying on it are also invalidated. This keeps the build process synchronized and prevents inconsistencies.

When you're writing or editing a Dockerfile, keep an eye out for unnecessary cache misses to ensure that builds run as fast and efficiently as possible.

## Try it out

In this hands-on guide, you will learn how to use the Docker build cache effectively for a Node.js application.

### Build the application

1. Download and install Docker Desktop.

2. Open a terminal and clone this sample application.

 [code example]

3. Navigate into the todo-list-app directory:

 [code example]

 Inside this directory, you'll find a file named Dockerfile with the following content:

 [code example]

4. Execute the following command to build the Docker image:

 [code example]

 Here’s the result of the build process:

 [code example]

 The first line indicates that the entire build process took *20.0 seconds*. The first build may take some time as it installs dependencies.

5. Rebuild without making changes.

 Now, re-run the docker build command without making any change in the source code or Dockerfile as shown:

 [code example]

 Subsequent builds after the initial are faster due to the caching mechanism, as long as the commands and context remain unchanged. Docker caches the intermediate layers generated during the build process. When you rebuild the image without making any changes to the Dockerfile or the source code, Docker can reuse the cached layers, significantly speeding up the build process.

 [code example]

 The subsequent build was completed in just 1.0 second by leveraging the cached layers. No need to repeat time-consuming steps like installing dependencies.

 
 
 
 Steps
 
 Description
 
 Time Taken (1st Run)
 
 Time Taken (2nd Run)
 
 
 
 
 
 1
 
 Load build definition from Dockerfile
 
 0.0 seconds
 
 0.0 seconds
 
 
 
 2
 
 Load metadata for docker.io/library/node:22-alpine
 
 2.7 seconds
 
 0.9 seconds
 
 
 
 3
 
 Load.dockerignore
 
 0.0 seconds
 
 0.0 seconds
 
 
 
 4
 
 Load build context
 
 (Context size: 4.60MB)
 
 0.1 seconds
 
 0.0 seconds
 
 
 
 5
 
 Set the working directory (WORKDIR)
 
 0.1 seconds
 
 0.0 seconds
 
 
 
 6
 
 Copy the local code into the container
 
 0.0 seconds
 
 0.0 seconds
 
 
 
 7
 
 Run yarn install --production
 
 10.0 seconds
 
 0.0 seconds
 
 
 
 8
 
 Exporting layers
 
 2.2 seconds
 
 0.0 seconds
 
 
 
 9
 
 Exporting the final image
 
 3.0 seconds
 
 0.0 seconds
 
 
 
 

 Going back to the docker image history output, you see that each command in the Dockerfile becomes a new layer in the image. You might remember that when you made a change to the image, the yarn dependencies had to be reinstalled. Is there a way to fix this? It doesn't make much sense to reinstall the same dependencies every time you build, right?

 To fix this, restructure your Dockerfile so that the dependency cache remains valid unless it really needs to be invalidated. For Node-based applications, dependencies are defined in the package.json file. You'll want to reinstall the dependencies if that file changes, but use cached dependencies if the file is unchanged. So, start by copying only that file first, then install the dependencies, and finally copy everything else. Then, you only need to recreate the yarn dependencies if there was a change to the package.json file.

6. Update the Dockerfile to copy in the package.json file first, install dependencies, and then copy everything else in.

 [code example]

7. Create a file named.dockerignore in the same folder as the Dockerfile with the following contents.

 [code example]

8. Build the new image:

 [code example]

 You'll then see output similar to the following:

 [code example]

 You'll see that all layers were rebuilt. Perfectly fine since you changed the Dockerfile quite a bit.

9. Now, make a change to the src/static/index.html file (like change the title to say "The Awesome Todo App").

10. Build the Docker image. This time, your output should look a little different.

 [code example]

 You'll then see output similar to the following:

 [code example]

 First off, you should notice that the build was much faster. You'll see that several steps are using previously cached layers. That's good news; you're using the build cache. Pushing and pulling this image and updates to it will be much faster as well.

By following these optimization techniques, you can make your Docker builds faster and more efficient, leading to quicker iteration cycles and improved development productivity.

## Additional resources

* Optimizing builds with cache management
* Cache Storage Backend
* Build cache invalidation

## Next steps

Now that you understand how to use the Docker build cache effectively, you're ready to learn about Multi-stage builds.