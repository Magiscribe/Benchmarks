# AI Models Update - October 11, 2025

## Summary
Updated the inference engine with the latest AI models from Anthropic, OpenAI, and Google based on official documentation as of October 2025.

## Changes Made

### Anthropic Claude Models
**Added:**
- `claude-4.1-opus` (claude-opus-4-1-20250805) - Advanced reasoning model for specialized complex tasks
- `claude-4.5-sonnet` (claude-sonnet-4-5-20250929) - **Best model for complex agents and coding** with highest intelligence across most tasks

**Kept for backward compatibility:**
- `claude-3-opus`, `claude-3-5-haiku`, `claude-3-5-sonnet` (deprecated), `claude-3-7-sonnet`, `claude-4-sonnet`, `claude-4-opus`

### OpenAI Models
**Added:**
- `gpt-5` (gpt-5) - **Latest flagship model** with extended access and highest performance
- `gpt-5-thinking` (gpt-5-thinking) - Extended reasoning capabilities
- `gpt-5-thinking-mini` (gpt-5-thinking-mini) - Efficient reasoning model
- `gpt-4o-mini` (gpt-4o-mini) - Cost-effective option
- `gpt-4.5` (gpt-4.5) - Pro-tier model with advanced capabilities

**Kept:**
- `gpt-4o`, `gpt-4.1`, `o3`, `o4-mini`

### Google Gemini Models
**Added:**
- `gemini-2.5-flash-lite` (gemini-2.5-flash-lite) - **Ultra fast, most cost-effective** with high throughput
- `gemini-2.0-flash` (gemini-2.0-flash) - Second generation workhorse with 1M token context
- `gemini-2.0-flash-lite` (gemini-2.0-flash-lite) - Fast and cost-effective second gen model

**Updated:**
- `gemini-2.5-pro` - Now uses stable endpoint (gemini-2.5-pro) instead of preview version
- `gemini-2.5-flash` - Now uses stable endpoint (gemini-2.5-flash) instead of preview version

### GROQ (No changes)
- `llama-4-maverick`, `llama-4-scout` - Kept as-is

## Model Recommendations

### Best Overall Performance
- **Claude 4.5 Sonnet** - Highest intelligence, best for complex agents and coding
- **GPT-5** - Latest flagship model from OpenAI

### Best for Reasoning
- **Claude Opus 4.1** - Exceptional for specialized complex tasks
- **GPT-5 Thinking** - Extended reasoning capabilities
- **OpenAI o3** - Advanced reasoning model

### Best Price-Performance
- **Gemini 2.5 Flash** - Balanced capabilities with good pricing
- **GPT-4o Mini** - Cost-effective OpenAI option
- **Gemini 2.5 Flash-Lite** - Ultra fast and cost-effective

### Fastest Options
- **Gemini 2.5 Flash-Lite** - Fastest in the 2.5 line
- **Claude 3.5 Haiku** - Fastest Claude model
- **GPT-5 Thinking Mini** - Fast reasoning

## Key Features

### Claude 4.5 Sonnet (claude-sonnet-4-5-20250929)
- Training data through July 2025
- Reliable knowledge through January 2025
- 200K context (1M beta available)
- 64K max output
- Extended thinking support
- $3/MTok input, $15/MTok output

### GPT-5
- Latest flagship model
- Supports thinking modes
- 32K-128K context depending on plan
- Access to GPT-5 Pro mode for hardest questions

### Gemini 2.5 Models
- **Pro**: Most advanced reasoning, best for complex problems in code/math/STEM
- **Flash**: Best price-performance, well-rounded capabilities
- **Flash-Lite**: Fastest, most cost-effective, 1M token context

## API Compatibility
All models maintain the same provider interface:
- **Anthropic**: Uses ANTHROPIC_API_KEY
- **OpenAI**: Uses OPENAI_API_KEY
- **Google**: Uses GOOGLE_API_KEY
- **GROQ**: Uses GROQ_API_KEY

No code changes required - just update your model selection!

## Next Steps
1. Test the new models with your existing benchmarks
2. Consider running comparative tests between Claude 4.5 Sonnet and GPT-5
3. Evaluate cost vs. performance for your use cases
4. Update any documentation that references specific model versions

## Sources
- [Anthropic Claude Models Documentation](https://docs.anthropic.com/en/docs/about-claude/models)
- [OpenAI Pricing and Models](https://openai.com/pricing/)
- [OpenAI API Platform](https://openai.com/api/)
- [Google Vertex AI Models](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)
- [Google AI Gemini Models](https://ai.google.dev/gemini-api/docs/models/gemini)
