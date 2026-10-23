You've deployed your application and exposed it via a Service. Now what? Kubernetes provides a
number of tools to help you manage your application deployment, including scaling and updating.

## Organizing resource configurations

Many applications require multiple resources to be created, such as a Deployment along with a Service.
Management of multiple resources can be simplified by grouping them together in the same file
(separated by --- in YAML). For example:

Multiple resources can be created the same way as a single resource:

[code example]

[code example]

The resources will be created in the order they appear in the manifest. Therefore, it's best to
specify the Service first, since that will ensure the scheduler can spread the pods associated
with the Service as they are created by the controller(s), such as Deployment.

 kubectl apply also accepts multiple -f arguments:

[code example]

It is a recommended practice to put resources related to the same microservice or application tier
into the same file, and to group all of the files associated with your application in the same
directory. If the tiers of your application bind to each other using DNS, you can deploy all of
the components of your stack together.

A URL can also be specified as a configuration source, which is handy for deploying directly from
manifests in your source control system:

[code example]

[code example]

If you need to define more manifests, such as adding a ConfigMap, you can do that too.

### External tools

This section lists only the most common tools used for managing workloads on Kubernetes. To see a larger list, view
Application definition and image build
in the Landscape.

#### Helm {#external-tool-helm}

Helm is a tool for managing packages of pre-configured
Kubernetes resources. These packages are known as _Helm charts_.

#### Kustomize {#external-tool-kustomize}

Kustomize traverses a Kubernetes manifest to add, remove or update configuration options.
It is available both as a standalone binary and as a native feature
of kubectl.

## Bulk operations in kubectl

Resource creation isn't the only operation that kubectl can perform in bulk. It can also extract
resource names from configuration files in order to perform other operations, in particular to
delete the same resources you created:

[code example]

[code example]

In the case of two resources, you can specify both resources on the command line using the
resource/name syntax:

[code example]

For larger numbers of resources, you'll find it easier to specify the selector (label query)
specified using -l or --selector, to filter resources by their labels:

[code example]

[code example]

### Chaining and filtering

Because kubectl outputs resource names in the same syntax it accepts, you can chain operations
using $() or xargs:

[code example]

The output might be similar to:

[code example]

With the above commands, first you create resources under docs/concepts/cluster-administration/nginx/ and print
the resources created with -o name output format (print each resource as resource/name).
Then you grep only the Service, and then print it with kubectl get.

### Recursive operations on local files

If you happen to organize your resources across several subdirectories within a particular
directory, you can recursively perform the operations on the subdirectories also, by specifying
 --recursive or -R alongside the --filename / -f argument.

For instance, assume there is a directory project/k8s/development that holds all of the
 needed for the development environment,
organized by resource type:

[code example]

By default, performing a bulk operation on project/k8s/development will stop at the first level
of the directory, not processing any subdirectories. If you had tried to create the resources in
this directory using the following command, we would have encountered an error:

[code example]

[code example]

Instead, specify the --recursive or -R command line argument along with the --filename / -f argument:

[code example]

[code example]

The --recursive argument works with any operation that accepts the --filename / -f argument such as:
 kubectl create, kubectl get, kubectl delete, kubectl describe, or even kubectl rollout.

The --recursive argument also works when multiple -f arguments are provided:

[code example]

[code example]

If you're interested in learning more about kubectl, go ahead and read
Command line tool (kubectl).

## Updating your application without an outage

At some point, you'll eventually need to update your deployed application, typically by specifying
a new image or image tag. kubectl supports several update operations, each of which is applicable
to different scenarios.

You can run multiple copies of your app, and use a _rollout_ to gradually shift the traffic to
new healthy Pods. Eventually, all the running Pods would have the new software.

This section of the page guides you through how to create and update applications with Deployments.

Let's say you were running version 1.14.2 of nginx:

[code example]

[code example]

Ensure that there is 1 replica:

[code example]

[code example]

and allow Kubernetes to add more temporary replicas during a rollout, by setting a _surge maximum_ of
100%:

[code example]

[code example]

To update to version 1.16.1, change.spec.template.spec.containers[0].image from nginx:1.14.2 
to nginx:1.16.1 using kubectl edit:

[code example]

That's it! The Deployment will declaratively update the deployed nginx application progressively
behind the scene. It ensures that only a certain number of old replicas may be down while they are
being updated, and only a certain number of new replicas may be created above the desired number
of pods. To learn more details about how this happens,
visit Deployment.

You can use rollouts with DaemonSets, Deployments, or StatefulSets.

### Managing rollouts

You can use kubectl rollout to manage a
progressive update of an existing application.

For example:

[code example]

or

[code example]

You can also pause, resume or cancel a rollout.
Visit kubectl rollout to learn more.

## Canary deployments

Another scenario where multiple labels are needed is to distinguish deployments of different
releases or configurations of the same component. It is common practice to deploy a *canary* of a
new application release (specified via image tag in the pod template) side by side with the
previous release so that the new release can receive live production traffic before fully rolling
it out.

For instance, you can use a track label to differentiate different releases.

The primary, stable release would have a track label with value as stable:

[code example]

and then you can create a new release of the guestbook frontend that carries the track label
with different value (i.e. canary ), so that two sets of pods would not overlap:

[code example]

The frontend service would span both sets of replicas by selecting the common subset of their
labels (i.e. omitting the track label), so that the traffic will be redirected to both
applications:

[code example]

You can tweak the number of replicas of the stable and canary releases to determine the ratio of
each release that will receive live production traffic (in this case, 3:1).
Once you're confident, you can update the stable track to the new application release and remove
the canary one.

To learn what's involved, follow the Deploy a Release Using a Canary Deployment tutorial.

## Updating annotations

Sometimes you would want to attach annotations to resources. Annotations are arbitrary
non-identifying metadata for retrieval by API clients such as tools or libraries.
This can be done with kubectl annotate. For example:

[code example]

[code example]

For more information, see annotations
and kubectl annotate.

## Scaling your application

When load on your application grows or shrinks, use kubectl to scale your application.
For instance, to decrease the number of nginx replicas from 3 to 1, do:

[code example]

[code example]

Now you only have one pod managed by the deployment.

[code example]

[code example]

To have the system automatically choose the number of nginx replicas as needed,
ranging from 1 to 3, do:

[code example]

[code example]

Now your nginx replicas will be scaled up and down as needed, automatically.

For more information, please see kubectl scale,
kubectl autoscale and
horizontal pod autoscaler document.

## In-place updates of resources

Sometimes it's necessary to make narrow, non-disruptive updates to resources you've created.

### kubectl apply

It is suggested to maintain a set of configuration files in source control
(see configuration as code),
so that they can be maintained and versioned along with the code for the resources they configure.
Then, you can use kubectl apply 
to push your configuration changes to the cluster.

This command will compare the version of the configuration that you're pushing with the previous
version and apply the changes you've made, without overwriting any automated changes to properties
you haven't specified.

[code example]

[code example]

To learn more about the underlying mechanism, read server-side apply.

### kubectl edit

Alternatively, you may also update resources with kubectl edit:

[code example]

This is equivalent to first get the resource, edit it in text editor, and then apply the
resource with the updated version:

[code example]

This allows you to do more significant changes more easily. Note that you can specify the editor
with your EDITOR or KUBE_EDITOR environment variables.

For more information, please see kubectl edit.

### kubectl patch

You can use kubectl patch to update API objects in place.
This subcommand supports JSON patch,
JSON merge patch, and strategic merge patch.

See
Update API Objects in Place Using kubectl patch
for more details.

## Disruptive updates

In some cases, you may need to update resource fields that cannot be updated once initialized, or
you may want to make a recursive change immediately, such as to fix broken pods created by a
Deployment. To change such fields, use replace --force, which deletes and re-creates the
resource. In this case, you can modify your original configuration file:

[code example]

[code example]

## 

- Learn about how to use kubectl for application introspection and debugging.