# Model configuration for shared inference engine

# Model definitions
# Format: {"display_name": "api_endpoint_name"}
MODELS = {
    # Anthropic Claude models - Latest as of October 2025
    "claude-3-opus": "claude-3-opus-20240229",
    "claude-3-5-haiku": "claude-3-5-haiku-20241022",
    "claude-3-5-sonnet": "claude-3-5-sonnet-20240620",  # Deprecated but kept
    "claude-3-7-sonnet": "claude-3-7-sonnet-20250219",
    "claude-4-sonnet": "claude-sonnet-4-20250514",
    "claude-4-opus": "claude-opus-4-20250514",
    "claude-4.1-opus": "claude-opus-4-1-20250805",  # NEW - Advanced reasoning
    "claude-4.5-sonnet": "claude-sonnet-4-5-20250929",  # NEW - Best for complex agents and coding
    
    # OpenAI models - Latest as of October 2025
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",  # NEW - Cost-effective option
    "gpt-5": "gpt-5",  # NEW - Best model for coding and agentic tasks
    "gpt-5-mini": "gpt-5-mini",  # NEW - Faster, cheaper version for well-defined tasks
    "gpt-5-nano": "gpt-5-nano",  # NEW - Fastest, cheapest for summarization and classification
    "gpt-5-thinking-mini": "gpt-5-thinking-mini",  # NEW - Efficient reasoning
    "o4-mini": "o4-mini",  # Fast reasoning model

    # Google Gemini models - Latest as of October 2025
    "gemini-2.5-pro": "gemini-2.5-pro",  # UPDATED - Most advanced reasoning
    "gemini-2.5-flash": "gemini-2.5-flash",  # UPDATED - Best price-performance
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",  # NEW - Ultra fast, cost-effective
    "gemini-2.0-flash": "gemini-2.0-flash",  # Previous generation workhorse
    "gemini-2.0-flash-lite": "gemini-2.0-flash-lite",  # NEW - Fast and cost-effective
    
    # GROQ - Llama models
    "llama-4-maverick": "meta-llama/llama-4-maverick-17b-128e-instruct",
    "llama-4-scout": "meta-llama/llama-4-scout-17b-16e-instruct",
    
    # xAI Grok models - Latest as of October 2025
    "grok-4": "grok-4",  # World's best model - $3/1M input, $15/1M output
    "grok-4-fast-reasoning": "grok-4-fast-reasoning",  # NEW - Cost-efficient with reasoning $0.20/1M input, $0.50/1M output
    "grok-4-fast-non-reasoning": "grok-4-fast-non-reasoning",  # NEW - Fastest without reasoning $0.20/1M input, $0.50/1M output
    "grok-code-fast-1": "grok-code-fast-1",  # NEW - Lightning fast for agentic coding $0.20/1M input, $1.50/1M output
    "grok-3": "grok-3",  # Flagship for enterprise tasks $3/1M input, $15/1M output
    "grok-3-mini": "grok-3-mini",  # Lightweight reasoning model $0.30/1M input, $0.50/1M output
}

# List of all available model names (for command line choices)
AVAILABLE_MODELS = list(MODELS.keys())