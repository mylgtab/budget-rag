This tutorial aims to introduce fundamental concepts of Docker Compose by guiding you through the development of a basic Python web application. 

Using the Flask framework, the application features a hit counter in Redis, providing a practical example of how Docker Compose can be applied in web development scenarios. The concepts demonstrated here should be understandable even if you're not familiar with Python. 

## Prerequisites

Make sure you have:

- Installed the latest version of Docker Compose
- A basic understanding of Docker concepts and how Docker works

## Step 1: Set up the project

1. Create a directory for the project:

 [code example]

2. Create app.py in your project directory and add the following:

 [code example]

 The app reads its Redis connection details from environment variables, with sensible defaults so it works out of the box.

3. Create requirements.txt in your project directory and add the following:

 [code example]

4. Create a Dockerfile :

 [code example]

 > [!IMPORTANT]
 >
 > Make sure the file is named Dockerfile with no extension. Some editors add .txt 
 > automatically, which causes the build to fail.

 For more information on how to write Dockerfiles, see the Dockerfile reference.

5. Create a .env file to hold configuration values:

 [code example]

 Compose automatically reads .env and makes these values available for interpolation
 in your compose.yaml . For this example the gains are modest, but in practice,
 keeping configuration out of the Compose file makes it easier to:
 - Change values across environments without editing YAML
 - Avoid committing secrets to version control
 - Reuse values across multiple services

6. Create a .dockerignore file to keep unnecessary files out of your build context:

 [code example]

 Docker sends everything in your project directory to the daemon when it builds an image.
 Without .dockerignore , that includes your .env file (which may contain secrets) and
 any cached Python bytecode. Excluding them keeps builds fast and avoids accidentally
 baking sensitive values into an image layer.

## Step 2: Define and start your services

Compose simplifies the control of your entire application stack, making it easy to manage services, networks, and volumes in a single YAML configuration file. 

1. Create compose.yaml in your project directory and paste the following:

 [code example]

 This Compose file defines two services: 

 - The web service uses an image that's built from the Dockerfile in the current directory. It maps port 8000 on the host to port 5000 on the container where Flask listens by default.

 - The redis service uses a public Redis image pulled from the Docker Hub registry.

 For more information on the compose.yaml file, see How Compose works.

2. Start up your application: 

 [code example]

 With a single command, you create and start all the services from your configuration file. Compose builds your web image, pulls the Redis image, and starts both containers. 

3. Open http://localhost:8000 . You should see:

 [code example]

 Refresh the page — the counter increments on each visit.

 This minimal setup works, but it has two problems you'll fix in the next steps:

 - Startup race: web starts at the same time as redis . If Redis isn't ready yet,
 the Flask app fails to connect and crashes.
 - No persistence: If you run docker compose down followed by docker compose up , the
 counter resets to zero. docker compose down removes the containers, and with them
 any data written to the container's writable layer. docker compose stop preserves
 the containers so data survives, but you can't rely on that in production where
 containers are regularly replaced.

4. Stop the stack before moving on:

 [code example]

## Step 3: Fix the startup race with health checks

To fix the startup race, Compose needs to wait until redis is confirmed healthy before
starting web .

1. Update compose.yaml :

 [code example]

 The healthcheck block tells Compose how to test whether Redis is ready:

 - test is the command Compose runs inside the container to check its health.
 redis-cli ping connects to Redis and expects a PONG response — if it gets one,
 the container is healthy.
 - start_period gives Redis 10 seconds to initialize before health checks begin.
 Any failures during this window don't count toward the retry limit.
 - interval runs the check every 5 seconds after the start period has elapsed.
 - timeout gives each check 3 seconds to respond before treating it as a failure.
 - retries sets how many consecutive failures are allowed before Compose marks the
 container as unhealthy. With interval: 5s and retries: 5 , Compose will wait up
 to 25 seconds before giving up.

2. Start the stack to confirm the ordering is fixed:

 [code example]

 You should see something similar to:

 [code example]

3. Open http://localhost:8000 to confirm the app is still working, then stop the stack before moving on:

 [code example]

## Step 4: Enable Compose Watch for live updates

Without Compose Watch, every code change requires you to stop the stack, rebuild the image, and restart the containers. Compose Watch eliminates that cycle by automatically syncing changes into your running container as you save files.

1. Update compose.yaml to add the develop.watch block to the web service:
 
 [code example]

 The watch block defines two rules:
 - The sync+restart action watches your project directory ( . ) on the host. When a file changes, Compose copies any changed files into /code inside the running container, then restarts the container. Because the container restarts with the updated files already in place, Flask starts up reading the new code directly — no manual rebuild or restart needed. 
 - The rebuild action on requirements.txt triggers a full image rebuild whenever you add a new dependency, since installing packages requires rebuilding the image, not just syncing files.
 
2. Start the stack with Watch enabled:

 [code example]

3. Make a live change. Open app.py and update the greeting:

 [code example]

4. Save the file. Compose Watch detects the change and syncs it immediately:

 [code example]

5. Refresh http://localhost:8000 . The updated greeting appears without any restart
 and the counter should still be incrementing.

6. Stop the stack before moving on:

 [code example]

 For more information on how Compose Watch works, see Use Compose Watch.

## Step 5: Persist data with named volumes

Each time you stop and restart the stack the visit counter resets to zero. Redis data
lives inside the container, so it disappears when the container is removed. A named
volume fixes this by storing the data on the host, outside the container lifecycle.

1. Update compose.yaml :

 [code example]

 The redis-data:/data entry under redis.volumes mounts the named volume at /data , the path where Redis
 writes its data files. The top-level volumes key registers it with Docker so it
 persists between compose down and compose up cycles.

2. Start the stack with docker compose up --watch and refresh http://localhost:8000 a few times to build up a count.

3. Tear down the stack with docker compose down and then bring it back up again with docker compose up --watch .

4. Open http://localhost:8000 — the counter continues from where it left off.

5. Now reset the counter with docker compose down -v . 

 The -v flag removes named volumes along with the containers. Use this intentionally — it permanently deletes the stored data.

## Step 6: Structure your project with multiple Compose files

As applications grow, a single compose.yaml becomes harder to maintain. The include 
top-level element lets you split services across multiple files while keeping them part of the
same application.

This is especially useful when different teams own different parts of the stack, or when
you want to reuse infrastructure definitions across projects.

1. Create a new file in your project directory called infra.yaml and move the Redis service and volume into it:

 [code example]

2. Update compose.yaml to include infra.yaml :

 [code example]

3. Run the application to confirm everything still works:

 [code example]

 Compose merges both files at startup. The web service can still reference redis 
 by name because all included services share the same default network.

 This is a simplified example, but it demonstrates the basic principle of include and how it can make it easier to modularize complex applications into sub-Compose files. For more information on include and working with multiple Compose files, see Working with multiple Compose files.

4. Stop the stack before moving on:

 [code example]

## Step 7: Inspect and debug your running stack

With a fully configured stack, you can observe what's happening inside your containers
without stopping anything. This step covers the core commands for inspecting the resolved configuration, streaming logs, and running commands
inside a running container.

Before starting the stack, verify that Compose has resolved your .env variables and
merged all files correctly:

[code example]

 docker compose config doesn't require the stack to be running — it works purely from
your files. A few things worth noting in the output:

- ${APP_PORT} , ${REDIS_HOST} , and ${REDIS_PORT} have all been replaced with the
 values from your .env file.
- Short-form port notation ( "8000:5000" ) is expanded into its canonical fields
 ( target , published , protocol ).
- The default network and volume names are made explicit, prefixed with the project name
 compose-demo .
- The output is the fully resolved configuration, with any files
 brought in via include merged into a single view.

Use docker compose config any time you want to confirm what Compose will actually
apply, especially when debugging variable substitution or working with multiple Compose files.

Now start the stack in detached mode so the terminal stays free for the commands that
follow:

[code example]

### Stream logs from all services

[code example]

The -f flag follows the log stream in real time, interleaving output from both
containers with color-coded service name prefixes. Refresh http://localhost:8000 a
few times and watch the Flask request logs appear. To follow logs for a single service,
pass its name:

[code example]

Press Ctrl+C to stop following logs. The containers keep running.

### Run commands inside a running container

 docker compose exec runs a command inside an already-running container without
starting a new one. This is the primary tool for live debugging.

#### Verify environment variables are set correctly

[code example]

[code example]

#### Test that the web container can reach Redis using the service name as the hostname

[code example]

[code example]

This uses the same redis library your app uses, so a True response confirms that
service discovery, networking, and the Redis connection are all working end to end.

#### Inspect the live value of the hit counter in Redis

[code example]

## Where to go next

- Explore the full list of Compose commands
- Explore the Compose file reference
- Check out the Learning Docker Compose video on LinkedIn Learning
- Learn how to set environment variables in Compose
- Learn how to package and distribute your Compose app