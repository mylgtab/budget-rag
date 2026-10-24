Compose Bridge supports model-aware deployments. It can deploy and configure Docker Model Runner, a lightweight service that hosts and serves machine LLMs.

This reduces manual setup for LLM-enabled services and keeps deployments consistent across Docker Desktop and Kubernetes environments.

If you have a models top-level element in your compose.yaml file, Compose Bridge:

- Automatically injects environment variables for each model’s endpoint and name.
- Configures model endpoints differently for Docker Desktop vs Kubernetes.
- Optionally deploys Docker Model Runner in Kubernetes when enabled in Helm values

## Configure model runner settings

When deploying using generated Helm Charts, you can control the model runner configuration through Helm values.

[code example]

## Deploying a model runner

### Docker Desktop

When modelRunner.enabled is false , Compose Bridge configures your workloads to connect to Docker Model Runner running on the host:

[code example]

The endpoint is automatically injected into your service containers.

### Kubernetes

When modelRunner.enabled is true , Compose Bridge uses the generated manifests to deploy Docker Model Runner in your cluster, including:

- Deployment: Runs the docker-model-runner container
- Service: Exposes port 80 (maps to container port 12434 )
- PersistentVolumeClaim : Stores model files

The modelRunner.enabled setting also determines the number of replicas for the in-cluster model-runner-deployment :

- When true , the Kubernetes deployment replica count is set to 1, and Docker Model Runner is deployed in the cluster.
- When false , the Kubernetes deployment replica count is 0 (no in-cluster Model Runner). On Docker Desktop, workloads still connect to the host Model Runner as described above.