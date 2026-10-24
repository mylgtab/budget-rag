Docker Model Runner provides several configuration options to tune model behavior,
memory usage, and inference performance. This guide covers the key settings and
how to apply them.

## Context size (context length)

The context size determines the maximum number of tokens a model can process in
a single request, including both the input prompt and generated output. This is
one of the most important settings affecting memory usage and model capabilities.

### Default context size

By default, Docker Model Runner uses a context size that balances capability with
resource efficiency:

| Engine | Default behavior |
|--------|------------------|
| llama.cpp | 4096 tokens |
| vLLM | Uses the model's maximum trained context size |

> [!NOTE]
> The actual default varies by model. Most models support between 2,048 and 8,192
> tokens by default. Some newer models support 32K, 128K, or even larger contexts.

### Configure context size

You can adjust context size per model using the docker model configure command:

[code example]

Or in a Compose file:

[code example]

### Context size guidelines

| Context size | Typical use case | Memory impact |
|--------------|------------------|---------------|
| 2,048 | Simple queries, short code snippets | Low |
| 4,096 | Standard conversations, medium code files | Moderate |
| 8,192 | Long conversations, larger code files | Higher |
| 16,384+ | Extended documents, multi-file context | High |

> [!IMPORTANT]
> Larger context sizes require more memory (RAM/VRAM). If you experience out-of-memory
> errors, reduce the context size. As a rough guide, each additional 1,000 tokens
> requires approximately 100-500 MB of additional memory, depending on the model size.

### Check a model's maximum context

To see a model's configuration including context size:

[code example]

> [!NOTE]
> The docker model inspect command shows the model's maximum supported context length
> (e.g., gemma3.context_length ), not the configured context size. The configured context
> size is what you set with docker model configure --context-size and represents the
> actual limit used during inference, which should be less than or equal to the model's
> maximum supported context length.

## Runtime flags

Runtime flags let you pass parameters directly to the underlying inference engine.
This provides fine-grained control over model behavior.

### Using runtime flags

Runtime flags can be provided through multiple mechanisms:

#### Using Docker Compose

In a Compose file:

[code example]

#### Using Command Line

With the docker model configure command:

[code example]

### Common llama.cpp parameters

These are the most commonly used llama.cpp parameters. You don't need to look up
the llama.cpp documentation for typical use cases.

#### Sampling parameters

| Flag | Description | Default | Range |
|------|-------------|---------|-------|
| --temp | Temperature for sampling. Lower = more deterministic, higher = more creative | 0.8 | 0.0-2.0 |
| --top-k | Limit sampling to top K tokens. Lower = more focused | 40 | 1-100 |
| --top-p | Nucleus sampling threshold. Lower = more focused | 0.9 | 0.0-1.0 |
| --min-p | Minimum probability threshold | 0.05 | 0.0-1.0 |
| --repeat-penalty | Penalty for repeating tokens | 1.1 | 1.0-2.0 |

 Example: Deterministic output (for code generation) 

[code example]

 Example: Creative output (for storytelling) 

[code example]

#### Performance parameters

| Flag | Description | Default | Notes |
|------|-------------|---------|-------|
| --threads | CPU threads for generation | Auto | Set to number of performance cores |
| --threads-batch | CPU threads for batch processing | Auto | Usually same as --threads |
| --batch-size | Batch size for prompt processing | 512 | Higher = faster prompt processing |
| --mlock | Lock model in memory | Off | Prevents swapping, requires sufficient RAM |
| --no-mmap | Disable memory mapping | Off | May improve performance on some systems |

 Example: Optimized for multi-core CPU 

[code example]

#### GPU parameters

| Flag | Description | Default | Notes |
|------|-------------|---------|-------|
| --n-gpu-layers | Layers to offload to GPU | All (if GPU available) | Reduce if running out of VRAM |
| --main-gpu | GPU to use for computation | 0 | For multi-GPU systems |
| --split-mode | How to split across GPUs | layer | Options: none , layer , row |

 Example: Partial GPU offload (limited VRAM) 

[code example]

#### Advanced parameters

| Flag | Description | Default |
|------|-------------|---------|
| --rope-scaling | RoPE scaling method | Auto |
| --rope-freq-base | RoPE base frequency | Model default |
| --rope-freq-scale | RoPE frequency scale | Model default |
| --no-prefill-assistant | Disable assistant pre-fill | Off |
| --reasoning-budget | Token budget for reasoning models | 0 (disabled) |

### vLLM parameters

When using the vLLM backend, different parameters are available.

Use --hf_overrides to pass HuggingFace model config overrides as JSON:

[code example]

## Configuration presets

Here are complete configuration examples for common use cases.

### Code completion (fast, deterministic)

[code example]

### Chat assistant (balanced)

[code example]

### Creative writing (high temperature)

[code example]

### Long document analysis (large context)

[code example]

### Low memory system

[code example]

## Environment-based configuration

You can also configure models via environment variables in containers:

| Variable | Description |
|----------|-------------|
| LLM_URL | Auto-injected URL of the model endpoint |
| LLM_MODEL | Auto-injected model identifier |

See Models and Compose for details on how these are populated.

## Reset configuration

Configuration set via docker model configure persists until the model is removed.
To reset configuration:

[code example]

Using -1 resets to the default value.

## What's next

- Inference engines - Learn about llama.cpp and vLLM
- API reference - API parameters for per-request configuration
- Models and Compose - Configure models in Compose applications