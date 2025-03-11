# openai_interaction.py

import logging
from openai import OpenAI
from config import API_CONFIG  # or get_config("api") if you prefer dynamic calls

logger = logging.getLogger(__name__)

# Create an OpenAI client from config
client = OpenAI(api_key=API_CONFIG["openai_api_key"])

def call_openai_api(prompt_text, model_name=None, temperature=None):
    """
    Generic function to call the OpenAI API with a given prompt.
    The defaults for model_name and temperature can be sourced from API_CONFIG.
    """
    # Fallback to values from config if none provided
    if model_name is None:
        model_name = API_CONFIG.get("openai_model", "gpt-4")
    if temperature is None:
        temperature = API_CONFIG.get("openai_temperature", 0)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error calling OpenAI ChatCompletion: {str(e)}")
        return ""
