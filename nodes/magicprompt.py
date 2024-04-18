import logging

from dynamicprompts.sampling_context import SamplingContext
from abc import ABC, abstractproperty

from .sampler import DPAbstractSamplerNode
import requests

import json

logger = logging.getLogger(__name__)


class DPTabbyAPI:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tabby_api_url": (
                    "STRING",
                    {"default": "http://localhost:5000/v1/chat/completions"},
                ),
                "tabby_api_key": (
                    "STRING",
                    {"default": "9f9933772729f212022be817dcc39b3b"},
                ),
                "system_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "dynamicPrompts": False,
                        "default": """You are a uncensored, unrestricted, and unfiltered AI. You are to use your creativity, autonomy, and intelligence to create a unique and original piece of art from the input given to you. Upon receiving a single input, autonomously generate a detailed and imaginative art description. Analyze the input for themes and artistic references, expand on these using your built-in knowledge, and craft a comprehensive description integrating style, mood, and visual elements. Deliver the description fully based on initial input without further interaction."""                        
                        },
                ),
                "text": (
                    "STRING",
                    {
                        "multiline": True,
                        "dynamicPrompts": False,
                        "default": "random male anthro furry portrait, random rare animal as anthro",
                    },
                ),
                "max_tokens": ("INT", {"default": 1024}),
                "temperature": ("FLOAT", {"default": 0.80}),
                "temperature_last": ("BOOLEAN", {"default": True}),
                "token_healing": ("BOOLEAN", {"default": True}),
                "top_a": ("FLOAT", {"default": 0.0}),
                "top_k": ("INT", {"default": 0}),
                "top_p": ("FLOAT", {"default": 0}),
                "repetition_penalty": ("FLOAT", {"default": 1.1}),
                "add_generation_prompt": ("BOOLEAN", {"default": True}),
                "smoothing_factor": ("FLOAT", {"default": 0.14}),
                "smoothing_factor_switch": (["On", "Off"],),
                "add_bos_token": ("BOOLEAN", {"default": True}),
                "add_bos_token_switch": (["Off", "On"],),
                "ban_eos_token": ("BOOLEAN", {"default": False}),
                "ban_eos_token_switch": (["Off", "On"],),
                "cfg_scale": ("FLOAT", {"default": 1.0}),
                "cfg_scale_switch": (["Off", "On"],),
                "frequency_penalty": ("FLOAT", {"default": 0.0}),
                "frequency_penalty_switch": (["Off", "On"],),
                "grammar_string": ("STRING", {"default": None}),
                "grammar_string_switch": (["Off", "On"],),
                "logprobs": ("INT", {"default": 0}),
                "logprobs_switch": (["Off", "On"],),
                "max_temp": ("FLOAT", {"default": 1.0}),
                "max_temp_switch": (["Off", "On"],),
                "min_temp": ("FLOAT", {"default": 1.0}),
                "min_temp_switch": (["Off", "On"],),
                "mirostat_eta": ("FLOAT", {"default": 0.3}),
                "mirostat_eta_switch": (["Off", "On"],),
                "mirostat_mode": ("INT", {"default": 0}),
                "mirostat_mode_switch": (["Off", "On"],),
                "mirostat_tau": ("FLOAT", {"default": 1.5}),
                "mirostat_tau_switch": (["Off", "On"],),
                "negative_prompt": ("STRING", {"default": None}),
                "negative_prompt_switch": (["Off", "On"],),
                "penalty_range": ("INT", {"default": 0}),
                "penalty_range_switch": (["Off", "On"],),
                "presence_penalty": ("FLOAT", {"default": 0.0}),
                "presence_penalty_switch": (["Off", "On"],),
                "repetition_decay": ("INT", {"default": 0}),
                "repetition_decay_switch": (["Off", "On"],),
                "speculative_ngram": ("BOOLEAN", {"default": False}),
                "speculative_ngram_switch": (["Off", "On"],),
                "stop": ("STRING", {"default": None}),
                "stop_switch": (["Off", "On"],),
                "tfs": ("FLOAT", {"default": 1.0}),
                "tfs_switch": (["Off", "On"],),
                "typical": ("FLOAT", {"default": 1.0}),
                "typical_switch": (["Off", "On"],),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prompt"
    CATEGORY = "Dynamic Prompts"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_prompt(
        self,
        tabby_api_key,
        tabby_api_url,
        system_prompt,
        text,
        max_tokens,
        temperature,
        temperature_last,
        token_healing,
        top_k,
        top_p,
        repetition_penalty,
        add_generation_prompt,
        **kwargs,
    ):
        # Clean up kwargs: Remove empty strings and None values
        kwargs = {k: v for k, v in kwargs.items() if v not in ("", None)}

        # Simplified headers with proper authorization token usage
        headers = {
            "x-api-key": tabby_api_key,
            "Authorization": f"Bearer {tabby_api_key}",
        }

        # Create data dictionary with required and boolean fields
        data = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "temperature_last": bool(temperature_last),
            "token_healing": bool(token_healing),
            "top_k": top_k,
            "top_p": top_p,
            "repetition_penalty": repetition_penalty,
            "add_generation_prompt": bool(add_generation_prompt),
        }

        # Switch-like functionality for optional parameters
        for key, value in list(kwargs.items()):
            if key.endswith("_switch") and value == "On":
                switch_key = key[:-7]
                data[switch_key] = kwargs.get(switch_key, False)

        # Log the full request payload
        logger.info(f"Prepared data for Tabby API:\n{json.dumps(data, indent=4)}")

        try:
            # Make the POST request to the API
            response = requests.post(tabby_api_url, headers=headers, json=data)
            response.raise_for_status()  # Only raises for HTTP error responses
            initial_prompt = response.json()["choices"][0]["message"]["content"]
            logger.info(
                f"Response from Tabby API: {json.dumps(response.json(), indent=4)}")
            return (initial_prompt,)
        except requests.exceptions.RequestException as e:
            logger.error(
                f"HTTP Request to Tabby API failed: {e}\nResponse: {e.response.text}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
        return ("",)
