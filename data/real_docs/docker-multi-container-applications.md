## Explanation

Starting up a single-container application is easy. For example, a Python script that performs a specific data processing task runs within a container with all its dependencies. Similarly, a Node.js application serving a static website with a small API endpoint can be effectively containerized with all its necessary libraries and dependencies. However, as applications grow in size, managing them as individual containers becomes more difficult.

Imagine the data processing Python script needs to connect to a database. Suddenly, you're now managing not just the script but also a database server within the same container. If the script requires user logins, you'll need an authentication mechanism, further bloating the container size. 

One best practice for containers is that each container should do one thing and do it well. While there are exceptions to this rule, avoid the tendency to have one container do multiple things.

Now you might ask, "Do I need to run these containers separately? If I run them separately, how shall I connect them all together?"

While docker run is a convenient tool for launching containers, it becomes difficult to manage a growing application stack with it. Here's why:

- Imagine running several docker run commands (frontend, backend, and database) with different configurations for development, testing, and production environments. It's error-prone and time-consuming.
- Applications often rely on each other. Manually starting containers in a specific order and managing network connections become difficult as the stack expands.
- Each application needs its docker run command, making it difficult to scale individual services. Scaling the entire application means potentially wasting resources on components that don't need a boost.
- Persisting data for each application requires separate volume mounts or configurations within each docker run command. This creates a scattered data management approach.
- Setting environment variables for each application through separate docker run commands is tedious and error-prone.

That's where Docker Compose comes to the rescue.

Docker Compose defines your entire multi-container application in a single YAML file called compose.yml . This file specifies configurations for all your containers, their dependencies, environment variables, and even volumes and networks. With Docker Compose:

- You don't need to run multiple docker run commands. All you need to do is define your entire multi-container application in a single YAML file. This centralizes configuration and simplifies management.
- You can run containers in a specific order and manage network connections easily.
- You can simply scale individual services up or down within the multi-container setup. This allows for efficient allocation based on real-time needs.
- You can implement persistent volumes with ease.
- It's easy to set environment variables once in your Docker Compose file.

By leveraging Docker Compose for running multi-container setups, you can build complex applications with modularity, scalability, and consistency at their core.

## Try it out

In this hands-on guide, you'll first see how to build and run a counter web application based on Node.js, an Nginx reverse proxy, and a Redis database using the docker run commands. You’ll also see how you can simplify the entire deployment process using Docker Compose.

### Set up

1. Get the sample application. If you have Git, you can clone the repository for the sample application. Otherwise, you can download the sample application. Choose one of the following options.

 
 

 Use the following command in a terminal to clone the sample application repository.

 [code example]
 
 Navigate into the nginx-node-redis directory:

 [code example]

 Inside this directory, you'll find two sub-directories - nginx and web .
 

 
 

 Download the source and extract it.

 

 Navigate into the nginx-node-redis-main directory:

 [code example]

 Inside this directory, you'll find two sub-directories - nginx and web .

 
 

2. Download and install Docker Desktop.

### Build the images

1. Navigate into the nginx directory to build the image by running the following command:

 [code example]

2. Navigate into the web directory and run the following command to build the first web image:
 
 [code example]

### Run the containers

1. Before you can run a multi-container application, you need to create a network for them all to communicate through. You can do so using the docker network create command:

 [code example]

2. Start the Redis container by running the following command, which will attach it to the previously created network and create a network alias (useful for DNS lookups):

 [code example]

3. Start the first web container by running the following command:

 [code example]

4. Start the second web container by running the following:

 [code example]
 
5. Start the Nginx container by running the following command:

 [code example]

 > [!NOTE]
 >
 > Nginx is typically used as a reverse proxy for web applications, routing traffic to backend servers. In this case, it routes to the Node.js backend containers (web1 or web2).

6. Verify the containers are up by running the following command:

 [code example]

 You will see output like the following: 

 [code example]

7. If you look at the Docker Desktop Dashboard, you can see the containers and dive deeper into their configuration.

 

8. With everything up and running, you can open http://localhost in your browser to see the site. Refresh the page several times to see the host that’s handling the request and the total number of requests:

 [code example]

 > [!NOTE]
 >
 > You might have noticed that Nginx, acting as a reverse proxy, likely distributes incoming requests in a round-robin fashion between the two backend containers. This means each request might be directed to a different container (web1 and web2) on a rotating basis. The output shows consecutive increments for both the web1 and web2 containers and the actual counter value stored in Redis is updated only after the response is sent back to the client.

9. You can use the Docker Desktop Dashboard to remove the containers by selecting the containers and selecting the Delete button.

 
 
## Simplify the deployment using Docker Compose

Docker Compose provides a structured and streamlined approach for managing multi-container deployments. As stated earlier, with Docker Compose, you don’t need to run multiple docker run commands. All you need to do is define your entire multi-container application in a single YAML file called compose.yml . Let’s see how it works.

Navigate to the root of the project directory. Inside this directory, you'll find a file named compose.yml . This YAML file is where all the magic happens. It defines all the services that make up your application, along with their configurations. Each service specifies its image, ports, volumes, networks, and any other settings necessary for its functionality.

1. Use the docker compose up command to start the application:

 [code example]

 When you run this command, you should see output similar to the following:

 [code example]

2. If you look at the Docker Desktop Dashboard, you can see the containers and dive deeper into their configuration.

 

3. Alternatively, you can use the Docker Desktop Dashboard to remove the containers by selecting the application stack and selecting the Delete button.

 

In this guide, you learned how easy it is to use Docker Compose to start and stop a multi-container application compared to docker run which is error-prone and difficult to manage.

## Additional resources

* docker container run CLI reference
* What is Docker Compose