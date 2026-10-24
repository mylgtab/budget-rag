Open WebUI is an open-source,
self-hosted web interface that provides a ChatGPT-like experience for local
AI models. You can connect it to Docker Model Runner to get a polished chat
interface for your models.

## Prerequisites

- Docker Model Runner enabled with TCP access
- A model pulled (e.g., docker model pull ai/llama3.2 )

## Quick start with Docker Compose

The easiest way to run Open WebUI with Docker Model Runner is using Docker Compose.

Create a compose.yaml file:

[code example]

Start the services:

[code example]

Open your browser to http://localhost:3000.

## Configuration options

### Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| OLLAMA_BASE_URL | URL of Docker Model Runner | Required |
| WEBUI_AUTH | Enable authentication | true |
| OPENAI_API_BASE_URL | Use OpenAI-compatible API instead | - |
| OPENAI_API_KEY | API key (use any value for DMR) | - |

### Using OpenAI-compatible API

If you prefer to use the OpenAI-compatible API instead of the Ollama API:

[code example]

## Network configuration

### Docker Desktop

On Docker Desktop, host.docker.internal automatically resolves to the host machine.
The previous example works without modification.

### Docker Engine (Linux)

On Docker Engine, you may need to configure the network differently:

[code example]

Or use the host gateway:

[code example]

## Using Open WebUI

### Select a model

1. Open http://localhost:3000
2. Select the model drop-down in the top-left
3. Select from your pulled models (they appear with ai/ prefix)

### Pull models through the UI

Open WebUI can pull models directly:

1. Select the model drop-down
2. Enter a model name: ai/llama3.2 
3. Select the download icon

### Chat features

Open WebUI provides:

- Multi-turn conversations with context
- Message editing and regeneration
- Code syntax highlighting
- Markdown rendering
- Conversation history and search
- Export conversations

## Complete example with multiple models

This example sets up Open WebUI with Docker Model Runner and pre-pulls several models:

[code example]

## Enabling authentication

For multi-user setups or security, enable authentication:

[code example]

On first visit, you'll create an admin account.

## Troubleshooting

### Models don't appear in the drop-down

1. Verify Docker Model Runner is accessible:
 [code example]

2. Check that models are pulled:
 [code example]

3. Verify the OLLAMA_BASE_URL is correct and accessible from the container.

### "Connection refused" errors

1. Ensure TCP access is enabled for Docker Model Runner.

2. On Docker Desktop, verify host.docker.internal resolves:
 [code example]

3. On Docker Engine, try using network_mode: host or the explicit host IP.

### Slow response times

1. First requests load the model into memory, which takes time.

2. Subsequent requests are much faster.

3. If consistently slow, consider:
 - Using a smaller model
 - Reducing context size
 - Checking GPU acceleration is working

### CORS errors

If running Open WebUI on a different host:

1. In Docker Desktop, go to Settings > AI
2. Add the Open WebUI URL to CORS Allowed Origins 

## Customization

### Custom system prompts

Open WebUI supports setting system prompts per model. Configure these in the UI under Settings > Models.

### Model parameters

Adjust model parameters in the chat interface:

1. Select the settings icon next to the model name
2. Adjust temperature, top-p, max tokens, etc.

These settings are passed through to Docker Model Runner.

## Running on a different port

To run Open WebUI on a different port:

[code example]

## What's next

- API reference - Learn about the APIs Open WebUI uses
- Configuration options - Tune model behavior
- IDE integrations - Connect other tools to DMR