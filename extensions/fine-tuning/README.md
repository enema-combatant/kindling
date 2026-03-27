# Extension: Fine-Tuning

*Train a model on your own data using QLoRA.*

**Status:** Roadmap (coming soon)

## What You'll Learn

- Preparing training data from your own documents and conversations
- QLoRA fine-tuning (4-bit quantized low-rank adaptation)
- Running training on cloud GPUs (Vast.ai, RunPod — ~$0.70/hr for an A100)
- GGUF quantization for local deployment
- Evaluating your fine-tuned model against the base model

## Prerequisites

- Completed Mission 04 (Specialization)
- NVIDIA GPU with 8+ GB VRAM, OR access to cloud GPU rental
- ~$5-10 for cloud GPU training time

## Why Fine-Tune?

Mission 04 showed you how to specialize an AI through RAG — giving it knowledge without changing the model itself. Fine-tuning goes further: it changes how the model *thinks*, not just what it *knows*.

Use fine-tuning when:
- RAG + good prompts aren't achieving the quality you need
- You want the model to adopt a specific style or personality
- You have domain-specific reasoning patterns (not just facts)
- You need the model to follow complex output formats reliably

## Planned Contents

1. Data preparation from your Mission 04 domain corpus
2. Training with Hugging Face + PEFT on Vast.ai
3. GGUF conversion with llama.cpp
4. Local deployment via Ollama custom model
5. A/B evaluation: base model vs. fine-tuned
