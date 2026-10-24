USB/IP enables you to share USB devices over the network, which can then be accessed from within Docker containers. This page focuses on sharing USB devices connected to the machine you run Docker Desktop on. You can repeat the following process to attach and use additional USB devices as needed.

> [!NOTE]
>
> Docker Desktop includes built-in drivers for many common USB devices but Docker can't guarantee every possible USB device works with this setup.

## Setup and use

### Step one: Run a USB/IP server

To use USB/IP, you need to run a USB/IP server. For this guide, the implementation provided by jiegec/usbip will be used.

1. Clone the repository.

 [code example]

2. Run the emulated Human Interface Device (HID) device example.

 [code example]

### Step two: Start a privileged Docker container

To attach the USB device, start a privileged Docker container with the PID namespace set to host :

[code example]

 --privileged gives the container full access to the host, and --pid=host allows it to share the host’s process namespace.

### Step three: Enter the mount namespace of PID 1

Inside the container, enter the mount namespace of the init process to gain access to the pre-installed USB/IP tools:

[code example]

### Step four: Use the USB/IP tools

Now you can use the USB/IP tools as you would on any other system:

#### List USB devices

To list exportable USB devices from the host:

[code example]

Expected output:

[code example]

#### Attach a USB device

To attach a specific USB device, or the emulated keyboard in this case:

[code example]

#### Verify device attachment

After attaching the emulated keyboard, check the /dev/input directory for the device node:

[code example]

Example output:

[code example]

### Step five: Access the device from another container

While the initial container remains running to keep the USB device operational, you can access the attached device from another container. For example:

1. Start a new container with the attached device.

 [code example]

2. Install a tool like evtest to test the emulated keyboard.

 [code example]

3. Interact with the device, and observe the output.

 Example output:

 [code example]

> [!IMPORTANT]
>
> The initial container must remain running to maintain the connection to the USB device. Exiting the container will stop the device from working.