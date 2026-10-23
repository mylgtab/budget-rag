Compose handles networking for you by default, but gives you fine-grained control when you need it. This page explains how the default network works and how containers discover each other by name. It also covers when and how to define custom networks, connect services across separate Compose projects, map custom hostnames, and debug connectivity issues.

## Default network and service discovery

By default, Compose sets up a single network for your app. Each container for a service joins the default network and is both reachable by other containers on that network, and discoverable by its service name. This network uses the bridge driver. To attach services to a different Compose network or an external one, see Specify custom networks. To change how a service uses the host network stack ( network_mode: host ), see Change the network mode.

For most development setups, the default network is sufficient. When you run docker compose up, Compose creates a network named _default and attaches all services to it. Each service registers its name with an internal DNS server, so containers can reach each other using the service name directly. No IP addresses or manual configuration is needed.

For example, suppose your app is in a directory called myapp, and your compose.yaml looks like this:

[code example]

Compose automatically connects all services to the default network, so you don't need to define networks explicitly in the Compose file.

When you run docker compose up, the following happens:

1. A network called myapp_default is created.
2. A container is created using web 's configuration. It joins myapp_default under the name web.
3. A container is created using db 's configuration. It joins myapp_default under the name db.

Each container can now look up the service name web or db and get back the appropriate container's IP address. The web service can connect to the database at postgres://db:5432. From the host machine, the same database is accessible at postgres://localhost:8001 if your container is running locally.

> [!TIP]
>
> Docker assigns container IP addresses dynamically from the network's subnet each time a container starts so they are not persisted across restarts or recreations. This means you should always reference services by name, not IP address. When containers are recreated, for example after a configuration change, they receive a new IP address. The service name stays stable.

Your app's network is given a name based on the "project name", which is taken from the name of the directory it lives in. You can override the project name with either the --project-name flag or the COMPOSE_PROJECT_NAME environment variable.

The HOST_PORT and CONTAINER_PORT serve different purposes. In the example above, for db, the HOST_PORT is 8001 and the container port is 5432 (the Postgres default). Networked service-to-service communication uses the CONTAINER_PORT. The host port is only used when accessing the service from outside the network.

### Updating containers on the network

If you make a configuration change to a service and run docker compose up to update it, the old container is removed and the new one joins the network under a different IP address but the same name. Running containers can look up that name and connect to the new address, but the old address stops working.

If any containers have connections open to the old container, they are closed. It is each container's responsibility to detect this condition, look up the name again, and reconnect.

## Change the network mode

By default, each service joins the project's bridge network. It is the most secure networking mode. If you don't specify network_mode, this is the type of network you are creating.

You can override the networking mode on a per-service basis. The network_mode option accepts the following values:

- host: The container shares the host's network stack. No port mapping is needed or supported, and service name DNS resolution does not work. Use for system-level tools like network monitors that require direct access to host interfaces. A container using network_mode: host can access all host ports and observe all network traffic on the host. Use it only when genuinely required.
- none: Turns off all container networking.
- service:{name}: Gives the container access to the specified container by referring to its service name.
- container:{name}: Gives the container access to the specified container by referring to its container ID.

You can mix modes in a single project:

[code example]

## Specify custom networks

Instead of just using the default app network, you can specify your own networks with the top-level networks key. This lets you create more complex topologies and specify custom network drivers and options. You can also use it to connect services to externally-created networks which aren't managed by Compose.

Each service can specify what networks to connect to with the service-level networks key, which is a list of names referencing entries under the top-level networks key.

The following example shows a Compose file which defines two custom networks. The proxy service is isolated from the db service, because they do not share a network in common. Only app can talk to both.

[code example]

Networks can be configured with static IP addresses by setting the ipv4_address and/or ipv6_address for each attached network.

Networks can also be given a custom name:

[code example]

### Internal networks

Setting internal: true on a network creates it without a connection to the host's network interfaces. It has no default gateway for external connectivity. This is useful for services like databases that should be completely unreachable from outside the container network:

[code example]

Note that a service connected to both an internal and a non-internal network (like worker above) can still reach the internet via the non-internal network public.

### Configure the default network

Instead of, or as well as, specifying your own networks, you can also change the settings of the app-wide default network by defining an entry under networks named default:

[code example]

## Use an existing external network

If you've manually created a bridge network using docker network create, you can connect your Compose services to it by marking the network as external:

[code example]

Instead of creating _default, Compose looks for a network called my-pre-existing-network and connects your containers to it.

### Connecting multiple Compose projects

External networks are particularly useful when services in separate Compose projects need to communicate. Create a shared network once, then reference it as external in each project:

[code example]

backend-compose.yaml:

[code example]

frontend-compose.yaml:

[code example]

Services on the same external network can reach each other by service name, just like services within a single project.

> [!IMPORTANT]
>
> The external network must exist before you run docker compose up. If it doesn't, Compose fails with a Network not found error. Always create it first with docker network create.

## Hybrid networking

A service can belong to both an external shared network and its own project-internal network. This lets you expose only the services that need to be reachable from other projects, while keeping everything else, such as databases, fully isolated:

[code example]

## Custom DNS with extra_hosts 

You can add custom hostname-to-IP mappings to a container's /etc/hosts file using extra_hosts. This is useful when a service needs to resolve a hostname that isn't registered in Docker's internal DNS. For example, a fixed-IP dependency or a staging endpoint:

[code example]

To map a hostname dynamically to the host machine's IP, use the special host-gateway value:

[code example]

On Linux, host-gateway resolves to the host's IP on the default bridge network. On Mac and Windows, Docker automatically provides this, host-gateway resolves to the same internal IP address as host.docker.internal.

You can also drive extra_hosts from environment variables, which makes it easy to point services at different targets per environment:

[code example]

Where.env.development might set API_HOST=localhost and a production env file might set API_HOST=10.0.1.50.

To verify what has been injected, inspect the hosts file inside the container:

[code example]

## Multi-host networking

When deploying a Compose application on a Docker Engine with Swarm mode enabled, you can use the built-in overlay driver to enable multi-host communication. Overlay networks are always created as attachable. You can optionally set the attachable property to false.

To learn more, see the overlay network driver documentation.

## Link containers

Links allow you to define extra aliases by which a service is reachable from another service. They are not required for basic service-to-service communication. By default, any service can reach any other service at that service's name. In the following example, db is reachable from web at both the hostnames db and database:

[code example]

See the links reference for more information.

## Debugging

When a service can't reach another, work through the following steps in order: first confirm the network configuration looks right, then confirm the containers are actually attached, then test live connectivity.

### Inspect port mappings

To find out which host port maps to a container port, use docker compose port:

[code example]

This is especially useful when using dynamic port mapping, where the host port changes on every docker compose up:

[code example]

[code example]

When you scale a service, each replica gets its own dynamic port. Use --index to query a specific replica:

[code example]

By default, docker compose port looks for TCP mappings. If a service exposes both TCP and UDP on the same port, use --protocol:

[code example]

### Verify network membership

To check which containers are attached to a network (useful when troubleshooting connectivity across external or custom networks):

[code example]

### Check connectivity

If the network membership looks correct but services still can't reach each other, test connectivity from inside a running container using docker compose exec.

## Further reference information

For full details of the network configuration options available, see the following references:

- Top-level networks element
- Service-level networks attribute