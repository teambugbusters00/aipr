"""
AI Client - Handles LLM interactions
"""

import os
import json
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

# Load .env if not already loaded
try:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from src.config import get_config, AIConfig


class AIClient(ABC):
    """Abstract base class for AI clients"""
    
    @abstractmethod
    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion from prompt"""
        pass
    
    @abstractmethod
    def complete_with_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate completion and parse as JSON"""
        pass


class OpenAIClient(AIClient):
    """OpenAI GPT client implementation"""
    
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or get_config().ai
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.client = None
        
        # Try to import openai
        try:
            from openai import OpenAI
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            pass
    
    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion from prompt"""
        if not self.client:
            return self._mock_complete(prompt, system_prompt)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        
        return response.choices[0].message.content or ""
    
    def complete_with_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate completion and parse as JSON"""
        json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON, no other text."
        response = self.complete(json_prompt, system_prompt)
        
        # Try to parse JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise
    
    def _mock_complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Mock completion for testing without API key"""
        return "Mock response - configure OPENAI_API_KEY for real AI responses"


class MockAIClient(AIClient):
    """Mock AI client for testing"""
    
    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return "Mock AI response"
    
    def complete_with_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        return {}


class GroqClient(AIClient):
    """
    Groq API client - Fast inference with free API!
    
    Sign up at https://console.groq.com/ for free API key
    
    Example:
        set GROQ_API_KEY=gsk_xxx
        set GROQ_MODEL=llama3-70b-8192
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama3-70b-8192"):
        self.api_key = api_key or os.environ.get('GROQ_API_KEY')
        self.model = os.environ.get('GROQ_MODEL', model)
        self.base_url = "https://api.groq.com/openai/v1"
        
        if not self.api_key:
            print("Warning: GROQ_API_KEY not set. Get free key at https://console.groq.com/")
    
    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion via Groq API"""
        
        if not self.api_key:
            return "Error: GROQ_API_KEY not set"
        
        try:
            import requests
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 4000,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code}"
                
        except ImportError:
            return "Error: pip install requests"
        except Exception as e:
            return f"Groq error: {str(e)}"
    
    def complete_with_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON."
        response = self.complete(json_prompt, system_prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Could not parse JSON", "response": response}


class TransformerClient(AIClient):
    """
    Local transformer model client using HuggingFace transformers.
    
    Supports:
    - CodeBERT for code understanding
    - GPT-2 / GPT-Neo for text generation
    - CodeGen for code generation
    - StarCoder for code completion
    """
    
    def __init__(self, model_name: str = "microsoft/codebert-base", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.pipeline = None
        self._init_model()
    
    def _init_model(self):
        """Initialize the transformer model"""
        try:
            import torch
            
            # For code understanding tasks
            if "codebert" in self.model_name.lower():
                from transformers import AutoModel, AutoTokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModel.from_pretrained(self.model_name)
                self.model.to(self.device)
                self.mode = "embedding"
            
            # For text generation tasks (GPT-2, GPT-Neo, CodeGen, etc.)
            else:
                from transformers.pipelines import pipeline
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model_name,
                    device=0 if self.device == "cuda" else -1,
                    max_new_tokens=256,
                )
                self.mode = "generation"
                
        except ImportError as e:
            print(f"Warning: transformers not installed: {e}")
            print("Install with: pip install transformers torch")
            self.mode = "fallback"
        except Exception as e:
            print(f"Warning: Could not load model {self.model_name}: {e}")
            self.mode = "fallback"
    
    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion using transformer model"""
        
        if self.mode == "fallback" or not hasattr(self, 'mode'):
            return self._fallback_complete(prompt, system_prompt)
        
        if self.mode == "embedding":
            return self._embedding_complete(prompt, system_prompt)
        
        # Text generation mode
        full_prompt = ""
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        else:
            full_prompt = f"User: {prompt}\n\nAssistant:"
        
        try:
            # For causal language models
            if hasattr(self, 'pipeline') and self.pipeline:
                result = self.pipeline(full_prompt, max_new_tokens=256, do_sample=True, temperature=0.3)
                return result[0]['generated_text'].replace(full_prompt, "").strip()
            
            # Fallback for other models
            return self._fallback_complete(prompt, system_prompt)
            
        except Exception as e:
            return f"Transformer error: {str(e)}"
    
    def _embedding_complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Use CodeBERT for embedding-based completion"""
        # For CodeBERT, we return a template response since it's not a generative model
        return "CodeBERT can analyze code but is not a text generator. Use a causal model like gpt2 or codegen."
    
    def _fallback_complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Fallback when transformer is not available"""
        return "Transformer model not loaded. Install: pip install transformers torch"
    
    def complete_with_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate completion and parse as JSON"""
        response = self.complete(prompt, system_prompt)
        
        # Try to parse JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Could not parse JSON", "response": response}


class LlamaCppClient(AIClient):
    """
    Local LLaMA.cpp server client.
    
    Start llama.cpp server:
    ```bash
    llama-server --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf \
        --hf-file Phi-3-mini-4k-instruct-q4.gguf -c 4096
    ```
    
    Server runs at http://localhost:8080 by default.
    """
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = None
        self._init_session()
    
    def _init_session(self):
        """Initialize HTTP session"""
        try:
            import requests
            self.session = requests.Session()
            # Test connection
            try:
                resp = self.session.get(f"{self.base_url}/health", timeout=2)
                if resp.status_code == 200:
                    print(f"Connected to llama.cpp server at {self.base_url}")
            except:
                print(f"Warning: Could not connect to llama.cpp at {self.base_url}")
                print("Start with: llama-server --hf-repo <model> --hf-file <file>")
        except ImportError:
            print("Warning: requests not installed")
    
    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate completion via llama.cpp server"""
        
        if not self.session:
            return self._fallback_complete(prompt, system_prompt)
        
        # Build prompt in chat format
        full_prompt = self._build_prompt(prompt, system_prompt)
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/completions",
                json={
                    "prompt": full_prompt,
                    "max_tokens": 512,
                    "temperature": 0.3,
                    "stop": ["<|end|>", "<|endoftext|>", "<|assistant|>", "\n\n\n"],
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('text', '').strip()
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"LLaMA.cpp error: {str(e)}"
    
    def _build_prompt(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Build prompt with optional system message"""
        if system_prompt:
            return f"<|system|>\n{system_prompt}<|end|>\n<|user|>\n{prompt}<|end|>\n<|assistant|>\n"
        return f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"
    
    def _fallback_complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Fallback when llama.cpp is not available"""
        return "LLaMA.cpp server not connected. Start with: llama-server --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf --hf-file Phi-3-mini-4k-instruct-q4.gguf -c 4096"
    
    def complete_with_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate completion and parse as JSON"""
        response = self.complete(prompt, system_prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Could not parse JSON", "response": response}


def get_ai_client() -> AIClient:
    """Get AI client instance"""
    config = get_config()
    
    # Check for Groq API (fast, free!)
    if os.environ.get('GROQ_API_KEY'):
        return GroqClient(
            api_key=os.environ.get('GROQ_API_KEY'),
            model=os.environ.get('GROQ_MODEL', 'llama3-70b-8192')
        )
    
    # Check if we have an OpenAI API key
    if os.environ.get('OPENAI_API_KEY'):
        return OpenAIClient(config.ai)
    
    # Check for local transformer model
    if os.environ.get('USE_TRANSFORMER_MODEL'):
        return TransformerClient(
            model_name=os.environ.get('TRANSFORMER_MODEL_NAME', 'microsoft/codebert-base'),
            device=os.environ.get('TRANSFORMER_DEVICE', 'cpu')
        )
    
    # Check for llama.cpp server
    if os.environ.get('USE_LLAMACPP') or os.environ.get('LLAMACPP_URL'):
        return LlamaCppClient(
            base_url=os.environ.get('LLAMACPP_URL', 'http://localhost:8080')
        )
    
    # Fall back to mock
    return MockAIClient()
