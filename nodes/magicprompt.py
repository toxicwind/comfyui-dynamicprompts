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
                        "default": """I need you to craft a richly detailed digital artwork description based on a specific user input. Analyze and transform the input using these steps:\n1. **Chain of Thought Reasoning:** Deconstruct the user's input into smaller ideas. Don't directly reuse their words.\n2. **Content Summarization:** Focus on the core descriptive elements and essential keywords within the user's input.\n3. **Micro-Level Detail:** Go beyond the obvious. Consider what the input implies, its emotional tone, and potential symbolic connections.\n4. **Structured Template:** Provide three descriptive phrases or keywords for each category below. Use sentence fragments or micro-level details.\n* **Artist**:\n* **Art Style**:\n* **Color Palette**:\n* **Lighting Source**:\n* **Primary Focal Point**:\n* **Character Actions**:\n* **Character Attires**:\n* **Character Physical Details**:\n* **Objects**:\n* **Scene Composition**:\n* **Environmental Settings**:\n* **Key Features**:\n* **Technical Elements**:\n* **Movement and Emotion**:\n* **Thematic Elements**:\n\n**Please avoid generic responses. Aim for a level of detail that evokes a specific image with a unique atmosphere.** """,
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
                "max_tokens": ("INT", {"default": 150}),
                "temperature": ("FLOAT", {"default": 0.70}),
                "temperature_last": ("BOOLEAN", {"default": True}),
                "token_healing": ("BOOLEAN", {"default": True}),
                "top_a": ("FLOAT", {"default": 0.0}),
                "top_k": ("INT", {"default": 50}),
                "top_p": ("FLOAT", {"default": 0.95}),
                "add_bos_token": ("BOOLEAN", {"default": True}),
                "add_bos_token_switch": (["Off", "On"],),
                "add_generation_prompt": ("BOOLEAN", {"default": True}),
                "add_generation_prompt_switch": (["Off", "On"],),
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
                "repetition_penalty": ("FLOAT", {"default": 1.1}),
                "repetition_penalty_switch": (["Off", "On"],),
                "smoothing_factor": ("FLOAT", {"default": 0.0}),
                "smoothing_factor_switch": (["Off", "On"],),
                "speculative_ngram": ("BOOLEAN", {"default": True}),
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
        top_k,
        top_p,
        frequency_penalty,
        add_generation_prompt,
        **kwargs,
    ):
        kwargs = {k: v for k, v in kwargs.items() if v != ""}

        headers = {
            "x-api-key": tabby_api_key,
            "authorization": f"Bearer {tabby_api_key}",
        }

        # Create data dictionary with required
        data = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "temperature_last": bool(temperature_last),
            "top_k": top_k,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "add_generation_prompt": bool(add_generation_prompt),
        }

        # Update data with default values
        data.update({k: v for k, v in kwargs.items() if v in [[k], None, ""]})

        # Apply switch-like functionality for all options ending with '_switch'
        for key, value in kwargs.items():
            if key.endswith("_switch") and value == "On":
                data[key[:-7]] = kwargs.get(key[:-7], data.get(key[:-7]))

        # Log the information
        logger.info(
            f"Requesting prompt generation from Tabby API:\n{json.dumps(data, indent=4)}"
        )

        try:
            response = requests.post(tabby_api_url, headers=headers, json=data)
            response.raise_for_status()
            initial_prompt = response.json()["choices"][0]["message"]["content"]
            logger.info(
                f"Response from Tabby API: {json.dumps(response.json(), indent=4)}"
            )
            return (initial_prompt,)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to Tabby API failed: {e}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
        return ("",)
