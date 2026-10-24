> [!NOTE]
>
> This page covers GPU passthrough to Linux containers using --gpus , which is
> only available on Windows with the WSL 2 backend. Other forms of GPU
> acceleration in Docker Desktop, such as GPU-accelerated inference in
> Docker Model Runner, are available on
> other platforms.

Docker Desktop for Windows supports NVIDIA GPU Paravirtualization (GPU-PV) on NVIDIA GPUs, allowing containers to access GPU resources for compute-intensive workloads like AI, machine learning, or video processing.

## Prerequisites

To enable WSL 2 GPU Paravirtualization, you need:

- A Windows machine with an NVIDIA GPU
- Up to date Windows 10 or Windows 11 installation
- Up to date drivers from NVIDIA supporting WSL 2 GPU Paravirtualization
- The latest version of the WSL 2 Linux kernel. Use wsl --update on the command line
- To make sure the WSL 2 backend is turned on in Docker Desktop

## Validate GPU support

To confirm GPU access is working inside Docker, run the following:

[code example]

This runs an n-body simulation benchmark on the GPU. The output will be similar to:

[code example]

## Run a real-world model: SmolLM2 with Docker Model Runner

Use Docker Model Runner to run the SmolLM2 LLM with vLLM and GPU acceleration:

[code example]

Check it's correctly installed:

[code example]

Run the model:

[code example]