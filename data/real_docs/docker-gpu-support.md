Compose services can define GPU device reservations if the Docker host contains such devices and the Docker Daemon is set accordingly. For this, make sure you install the prerequisites if you haven't already done so.

The examples in the following sections focus specifically on providing service containers access to GPU devices with Docker Compose. 

## Enabling GPU access to service containers

GPUs are referenced in a compose.yaml file using the device attribute from the Compose Deploy specification, within your services that need them.

This provides more granular control over a GPU reservation as custom values can be set for the following device properties: 

- capabilities . This value is specified as a list of strings. For example, capabilities: [gpu] . You must set this field in the Compose file. Otherwise, it returns an error on service deployment.
- count . Specified as an integer or the value all , represents the number of GPU devices that should be reserved (providing the host holds that number of GPUs). If count is set to all or not specified, all GPUs available on the host are used by default.
- device_ids . This value, specified as a list of strings, represents GPU device IDs from the host. You can find the device ID in the output of nvidia-smi on the host. If no device_ids are set, all GPUs available on the host are used by default.
- driver . Specified as a string, for example driver: 'nvidia' 
- options . Key-value pairs representing driver specific options.

> [!IMPORTANT]
>
> You must set the capabilities field. Otherwise, it returns an error on service deployment.

> [!NOTE]
>
> count and device_ids are mutually exclusive. You must only define one field at a time.

For more information on these properties, see the Compose Deploy Specification.

### Example of a Compose file for running a service with access to 1 GPU device

[code example]

Run with Docker Compose:

[code example]

On machines hosting multiple GPUs, the device_ids field can be set to target specific GPU devices and count can be used to limit the number of GPU devices assigned to a service container. 

You can use count or device_ids in each of your service definitions. An error is returned if you try to combine both, specify an invalid device ID, or use a value of count that’s higher than the number of GPUs in your system.

[code example]

## Access specific devices

To allow access only to GPU-0 and GPU-3 devices:

[code example]