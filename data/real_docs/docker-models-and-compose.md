Compose lets you define AI models as core components of your application, so you can declare model dependencies alongside services and run the application on any platform that supports the Compose Specification.

## Prerequisites

- Docker Compose v2.38 or later
- A platform that supports Compose models such as Docker Model Runner (DMR).

## What are Compose models?

Compose models are a standardized way to define AI model dependencies in your application. By using the models top-level element in your Compose file, you can:

- Declare which AI models your application needs
- Specify model configurations and requirements
- Make your application portable across different platforms
- Let the platform handle model provisioning and lifecycle management

## Basic model definition

To define models in your Compose application, use the models top-level element:

[code example]

This example defines:
- A service called chat-app that uses a model named llm 
- A model definition for llm that references the ai/smollm2 model image

## Model configuration options

Models support various configuration options:

[code example]

Common configuration options include:
- model (required): The OCI artifact identifier for the model. This is what Compose pulls and runs via the model runner.
- context_size : Defines the maximum token context size for the model.

 > [!NOTE]
 > Each model has its own maximum context size. When increasing the context length,
 > consider your hardware constraints. In general, try to keep context size
 > as small as feasible for your specific needs.

- runtime_flags : A list of raw command-line flags passed to the inference engine when the model is started.
 See Configuration options for commonly used parameters and examples.
- Platform-specific options may also be available via extension attributes x-* 

> [!TIP]
> See more example in the Common runtime configurations section.

## Service model binding

Services can reference models in two ways: short syntax and long syntax.

### Short syntax

The short syntax is the simplest way to bind a model to a service:

[code example]

With short syntax, the platform automatically generates environment variables based on the model name:
- LLM_URL - URL to access the LLM model
- LLM_MODEL - Model identifier for the LLM model
- EMBEDDING_MODEL_URL - URL to access the embedding-model
- EMBEDDING_MODEL_MODEL - Model identifier for the embedding-model

### Long syntax

The long syntax allows you to customize environment variable names:

[code example]

With this configuration, your service receives:
- AI_MODEL_URL and AI_MODEL_NAME for the LLM model
- EMBEDDING_URL and EMBEDDING_NAME for the embedding model

## Platform portability

One of the key benefits of using Compose models is portability across different platforms that support the Compose specification.

### Docker Model Runner

When Docker Model Runner is enabled:

[code example]

Docker Model Runner will:
- Pull and run the specified model locally
- Provide endpoint URLs for accessing the model
- Inject environment variables into the service

### Cloud providers

The Compose models specification is portable. Platforms that implement the Compose specification can support the models top-level element, allowing the same Compose file to run on different infrastructure. Cloud-specific behavior can be configured using extension attributes ( x-* ):

[code example]

How a platform handles model definitions depends on its implementation. A platform might:

- Use managed AI services instead of running models locally
- Apply platform-specific optimizations and scaling
- Provide additional monitoring and logging capabilities
- Handle model versioning and updates automatically

## Common runtime configurations

Below are some example configurations for various use cases.

### Development

[code example]

### Conservative with disabled reasoning

[code example]

### Creative with high randomness

[code example]

### Highly deterministic

[code example]

### Concurrent processing

[code example]

### Rich vocabulary model

[code example]

### Embeddings

When using embedding models with the /v1/embeddings endpoint, you must include the --embeddings runtime flag for the model to be properly configured.

[code example]

## Reference

- models top-level element
- models attribute
- Docker Model Runner documentation
- Configuration options - Context size and runtime parameters
- Inference engines - llama.cpp and vLLM details
- API reference - OpenAI and Ollama-compatible APIs