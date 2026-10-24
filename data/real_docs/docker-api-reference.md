Once Model Runner is enabled, new API endpoints are available. You can use
these endpoints to interact with a model programmatically. Docker Model Runner
provides compatibility with OpenAI, Anthropic, and Ollama API formats.

## Determine the base URL

The base URL to interact with the endpoints depends on how you run Docker and
which API format you're using.

| Access from | Base URL |
|-------------|----------|
| Containers | http://model-runner.docker.internal |
| Host processes (TCP) | http://localhost:12434 |

> [!NOTE]
> TCP host access must be enabled. See Enable Docker Model Runner.

| Access from | Base URL |
|-------------|----------|
| Containers | http://172.17.0.1:12434 |
| Host processes | http://localhost:12434 |

> [!NOTE]
> The 172.17.0.1 interface may not be available by default to containers
 within a Compose project.
> In this case, add an extra_hosts directive to your Compose service YAML:
>
> [code example]
> Then you can access the Docker Model Runner APIs at http://model-runner.docker.internal:12434/ 

### Base URLs for third-party tools

When configuring third-party tools that expect OpenAI-compatible APIs, use these base URLs:

| Tool type | Base URL format |
|-----------|-----------------|
| OpenAI SDK / clients | http://localhost:12434/engines/v1 |
| Anthropic SDK / clients | http://localhost:12434 |
| Ollama-compatible clients | http://localhost:12434 |

See IDE and tool integrations for specific configuration examples.

## Supported APIs

Docker Model Runner supports multiple API formats:

| API | Description | Use case |
|-----|-------------|----------|
| OpenAI API | OpenAI-compatible chat completions, embeddings | Most AI frameworks and tools |
| Anthropic API | Anthropic-compatible messages endpoint | Tools built for Claude |
| Ollama API | Ollama-compatible endpoints | Tools built for Ollama |
| Image Generation API | Diffusers-based image generation | Generating images from text prompts |
| DMR API | Native Docker Model Runner endpoints | Model management |

## OpenAI-compatible API

DMR implements the OpenAI API specification for maximum compatibility with existing tools and frameworks.

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /engines/v1/models | GET | List models |
| /engines/v1/models/{namespace}/{name} | GET | Retrieve model |
| /engines/v1/chat/completions | POST | Create chat completion |
| /engines/v1/completions | POST | Create completion |
| /engines/v1/embeddings | POST | Create embeddings |

> [!NOTE]
> You can optionally include the engine name in the path: /engines/llama.cpp/v1/chat/completions .
> This is useful when running multiple inference engines.

### Model name format

When specifying a model in API requests, use the full model identifier including the namespace:

[code example]

Common model name formats:
- Docker Hub models: ai/smollm2 , ai/llama3.2 , ai/qwen2.5-coder 
- Tagged versions: ai/smollm2:360M-Q4_K_M 
- Custom models: myorg/mymodel 

### Supported parameters

The following OpenAI API parameters are supported:

| Parameter | Type | Description |
|-----------|------|-------------|
| model | string | Required. The model identifier. |
| messages | array | Required for chat completions. The conversation history. |
| prompt | string | Required for completions. The prompt text. |
| max_tokens | integer | Maximum tokens to generate. |
| temperature | float | Sampling temperature (0.0-2.0). |
| top_p | float | Nucleus sampling parameter (0.0-1.0). |
| stream | Boolean | Enable streaming responses. |
| stop | string/array | Stop sequences. |
| presence_penalty | float | Presence penalty (-2.0 to 2.0). |
| frequency_penalty | float | Frequency penalty (-2.0 to 2.0). |

### Limitations and differences from OpenAI

Be aware of these differences when using DMR's OpenAI-compatible API:

| Feature | DMR behavior |
|---------|--------------|
| API key | Not required. DMR ignores the Authorization header. |
| Function calling | Supported with llama.cpp for compatible models. |
| Vision | Supported for multi-modal models (e.g., LLaVA). |
| JSON mode | Supported via response_format: {"type": "json_object"} . |
| Logprobs | Supported. |
| Token counting | Uses the model's native token encoder, which may differ from OpenAI's. |

## Anthropic-compatible API

DMR provides Anthropic Messages API compatibility for tools and frameworks built for Claude.

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /anthropic/v1/messages | POST | Create a message |
| /anthropic/v1/messages/count_tokens | POST | Count tokens |

### Supported parameters

The following Anthropic API parameters are supported:

| Parameter | Type | Description |
|-----------|------|-------------|
| model | string | Required. The model identifier. |
| messages | array | Required. The conversation messages. |
| max_tokens | integer | Maximum tokens to generate. |
| temperature | float | Sampling temperature (0.0-1.0). |
| top_p | float | Nucleus sampling parameter. |
| top_k | integer | Top-k sampling parameter. |
| stream | Boolean | Enable streaming responses. |
| stop_sequences | array | Custom stop sequences. |
| system | string | System prompt. |

### Example: Chat with Anthropic API

[code example]

### Example: Streaming response

[code example]

## Ollama-compatible API

DMR also provides Ollama-compatible endpoints for tools and frameworks built for Ollama.

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/tags | GET | List available models |
| /api/show | POST | Show model information |
| /api/chat | POST | Generate chat completion |
| /api/generate | POST | Generate completion |
| /api/embeddings | POST | Generate embeddings |

### Example: Chat with Ollama API

[code example]

### Example: List models

[code example]

## Image generation API (Diffusers)

DMR supports image generation through the Diffusers backend, enabling you to generate
images from text prompts using models like Stable Diffusion.

> [!NOTE]
> The Diffusers backend requires an NVIDIA GPU with CUDA support and is only
> available on Linux (x86_64 and ARM64). See Inference engines
> for setup instructions.

### Endpoint

| Endpoint | Method | Description |
|----------|--------|-------------|
| /engines/diffusers/v1/images/generations | POST | Generate an image from a text prompt |

### Supported parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| model | string | Required. The model identifier (e.g., stable-diffusion:Q4 ). |
| prompt | string | Required. The text description of the image to generate. |
| size | string | Image dimensions in WIDTHxHEIGHT format (e.g., 512x512 ). |

### Response format

The API returns a JSON response with the generated image encoded in base64:

[code example]

### Example: Generate an image

[code example]

This command:
1. Sends a POST request to the Diffusers image generation endpoint
2. Specifies the model, prompt, and output image size
3. Extracts the base64-encoded image from the response using jq 
4. Decodes the base64 data and saves it as image.png 

## DMR native endpoints

These endpoints are specific to Docker Model Runner for model management:

| Endpoint | Method | Description |
|----------|--------|-------------|
| /models/create | POST | Pull/create a model |
| /models | GET | List local models |
| /models/{namespace}/{name} | GET | Get model details |
| /models/{namespace}/{name} | DELETE | Delete a local model |

## REST API examples

### Request from within a container

To call the chat/completions OpenAI endpoint from within another container using curl :

[code example]

### Request from the host using TCP

To call the chat/completions OpenAI endpoint from the host via TCP:

1. Enable the host-side TCP support from the Docker Desktop GUI, or via the Docker Desktop CLI.
 For example: docker desktop enable model-runner --tcp .

 If you are running on Windows, also enable GPU-backed inference.
 See Enable Docker Model Runner.

1. Interact with it as documented in the previous section using localhost and the correct port.

[code example]

### Request from the host using a Unix socket

To call the chat/completions OpenAI endpoint through the Docker socket from the host using curl :

[code example]

### Streaming responses

To receive streaming responses, set stream: true :

[code example]

## Using with OpenAI SDKs

### Python

[code example]

### Node.js

[code example]

## What's next

- IDE and tool integrations - Configure Cline, Continue, Cursor, and other tools
- Configuration options - Adjust context size and runtime parameters
- Inference engines - Learn about llama.cpp, vLLM, and Diffusers options