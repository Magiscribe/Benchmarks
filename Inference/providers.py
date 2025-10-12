from abc import ABC, abstractmethod

class VisionProvider(ABC):
    def __init__(self, model_name, api_key):
        self.model_name = model_name
        self.api_key = api_key
        self.client = self.get_client(api_key)

    @abstractmethod
    def run_model_on_image(self, encoded_image, system_prompt, user_prompt):
        pass

    @classmethod
    @abstractmethod
    def get_env_var_name(cls):
        pass

    @abstractmethod
    def get_client(self, api_key):
        pass

# Anthropic provider implementation
import anthropic
class AnthropicProvider(VisionProvider):
    @classmethod
    def get_env_var_name(cls):
        return "ANTHROPIC_API_KEY"

    def get_client(self, api_key):
        return anthropic.Anthropic(api_key=api_key)

    def run_model_on_image(self, encoded_image, system_prompt, user_prompt):
        response = self.client.messages.create(
            model=self.model_name,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encoded_image}}
                    ]
                }
            ],
            temperature=0,
            max_tokens=1000
        )
        return response.content[0].text
    
    def run_text_only(self, system_prompt, user_prompt):
        """Run text-only conversation without images."""
        response = self.client.messages.create(
            model=self.model_name,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0,
            max_tokens=1000
        )
        return response.content[0].text

# OpenAI provider implementation
import openai
class OpenAIProvider(VisionProvider):
    @classmethod
    def get_env_var_name(cls):
        return "OPENAI_API_KEY"

    def get_client(self, api_key):
        return openai.OpenAI(api_key=api_key)

    def run_model_on_image(self, encoded_image, system_prompt, user_prompt):
        # GPT-5 and newer reasoning models use max_completion_tokens instead of max_tokens
        uses_completion_tokens = any(x in self.model_name.lower() for x in ['gpt-5', 'o3', 'o4'])
        
        params = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
                ]}
            ]
        }
        
        # GPT-5 only supports default temperature (1), other models can use temperature=0
        if 'gpt-5' not in self.model_name.lower():
            params["temperature"] = 0
        
        # Use the appropriate parameter based on model
        # GPT-5 models need more tokens due to their reasoning process
        if uses_completion_tokens:
            params["max_completion_tokens"] = 16000
        else:
            params["max_tokens"] = 4000
        
        response = self.client.chat.completions.create(**params)
        
        content = response.choices[0].message.content
        if not content or len(content.strip()) == 0:
            raise ValueError(f"OpenAI returned empty content. Finish reason: {response.choices[0].finish_reason}. Model: {response.model}")
        
        return content
    
    def run_text_only(self, system_prompt, user_prompt):
        """Run text-only conversation without images."""
        # GPT-5 and newer reasoning models use max_completion_tokens instead of max_tokens
        uses_completion_tokens = any(x in self.model_name.lower() for x in ['gpt-5', 'o3', 'o4'])
        
        params = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        # GPT-5 only supports default temperature (1), other models can use temperature=0
        if 'gpt-5' not in self.model_name.lower():
            params["temperature"] = 0
        
        # Use the appropriate parameter based on model
        # GPT-5 models need more tokens due to their reasoning process
        if uses_completion_tokens:
            params["max_completion_tokens"] = 16000
        else:
            params["max_tokens"] = 4000
        
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content

# Google provider implementation - CORRECTED
try:
    from google.genai import Client
    from google.genai import types
    genai_available = True
except ImportError:
    genai_available = False

class GoogleProvider(VisionProvider):
    @classmethod
    def get_env_var_name(cls):
        return "GOOGLE_API_KEY"

    def get_client(self, api_key):
        if not genai_available:
            raise ImportError("google-genai is not installed. Please install it to use Gemini.")
        return Client(api_key=api_key)

    def run_model_on_image(self, encoded_image, system_prompt, user_prompt):
        # Convert base64 to bytes
        import base64
        image_bytes = base64.b64decode(encoded_image)
        
        # Create image part using keyword arguments
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        
        # Create text part using keyword arguments
        text_part = types.Part.from_text(text=system_prompt + "\n" + user_prompt)
        
        # Generate content using new SDK structure
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[text_part, image_part]
        )
        
        return response.text
    
    def run_text_only(self, system_prompt, user_prompt):
        """Run text-only conversation without images."""
        text_part = types.Part.from_text(text=system_prompt + "\n" + user_prompt)
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[text_part]
        )
        
        return response.text

# GROQ provider implementation
try:
    from groq import Groq
    groq_available = True
except ImportError:
    groq_available = False

class GroqProvider(VisionProvider):
    @classmethod
    def get_env_var_name(cls):
        return "GROQ_API_KEY"

    def get_client(self, api_key):
        if not groq_available:
            raise ImportError("groq is not installed. Please install it to use GROQ models.")
        return Groq(api_key=api_key)

    def run_model_on_image(self, encoded_image, system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{system_prompt}\n\n{user_prompt}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,
            max_completion_tokens=1000,
            top_p=1,
            stream=False,
            stop=None,
        )
        return response.choices[0].message.content
    
    def run_text_only(self, system_prompt, user_prompt):
        """Run text-only conversation without images."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0,
            max_completion_tokens=1000,
            top_p=1,
            stream=False,
            stop=None,
        )
        return response.choices[0].message.content

# xAI Grok provider implementation (OpenAI-compatible API)
class GrokProvider(VisionProvider):
    @classmethod
    def get_env_var_name(cls):
        return "XAI_API_KEY"

    def get_client(self, api_key):
        import openai
        # Grok uses OpenAI-compatible API with custom base URL
        return openai.OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )

    def run_model_on_image(self, encoded_image, system_prompt, user_prompt):
        params = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
                ]}
            ],
            "max_tokens": 4000,
            "temperature": 0
        }
        
        response = self.client.chat.completions.create(**params)
        
        content = response.choices[0].message.content
        if not content or len(content.strip()) == 0:
            raise ValueError(f"Grok returned empty content. Finish reason: {response.choices[0].finish_reason}. Model: {response.model}")
        
        return content
    
    def run_text_only(self, system_prompt, user_prompt):
        """Run text-only conversation without images."""
        params = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0
        }
        
        response = self.client.chat.completions.create(**params)
        
        content = response.choices[0].message.content
        if not content or len(content.strip()) == 0:
            raise ValueError(f"Grok returned empty content. Finish reason: {response.choices[0].finish_reason}. Model: {response.model}")
        
        return content

# Provider registry for easy lookup
PROVIDER_REGISTRY = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "gemini": GoogleProvider,
    "groq": GroqProvider,
    "grok": GrokProvider,
}
