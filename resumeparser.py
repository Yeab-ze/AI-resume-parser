# import libraries
from openai import OpenAI
import json
import re
import yaml
import os
import time

CONFIG_PATH = "config.yaml"

def _load_api_key():
    """Load API key from config.yaml or environment variables."""
    api_key = None

    # Try config file first
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as file:
                config_data = yaml.load(file, Loader=yaml.FullLoader)
                api_key = config_data.get('OPENROUTER_API_KEY') or config_data.get('OPENAI_API_KEY')
        except Exception as e:
            print(f"Warning: Could not read config.yaml: {e}")

    # Fall back to environment variables
    if not api_key or api_key.strip() in ["YOUR KEY HERE", "your_api_key_here", ""]:
        api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('OPENAI_API_KEY')

    return api_key


def _clean_and_parse_json(raw: str) -> dict:
    """
    Robustly extract and parse a JSON object from a model response
    that may contain markdown fences, extra text, or minor syntax errors.
    """
    if not raw or not raw.strip():
        raise ValueError("Empty response from model")

    text = raw.strip()

    # 1. Strip markdown fences (```json ... ``` or ``` ... ```)
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    # 2. Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 3. Extract the first {...} block from the text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

        # 4. Fix common issues: trailing commas before } or ]
        fixed = re.sub(r',\s*([}\]])', r'\1', candidate)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from response:\n{raw[:500]}")


def ats_extractor(resume_data: str, job_description: str = None) -> dict:
    """
    Extract structured ATS information from resume text using an LLM.
    Returns a dict with parsed fields, or a dict with an 'error' key on failure.
    """
    api_key = _load_api_key()

    if not api_key:
        return {
            "error": "API key is missing. Add OPENROUTER_API_KEY or OPENAI_API_KEY to config.yaml or set it as an environment variable."
        }

    # Build prompt
    jd_note = f"\n\nJob Description to match against:\n{job_description}" if job_description else ""
    prompt = f"""You are a professional resume parser. Extract information from the resume and return ONLY a valid JSON object — no markdown, no explanation, no extra text before or after.

The JSON must have exactly these keys:
{{
  "full_name": "string or null",
  "email": "string or null",
  "github": "string or null",
  "linkedin": "string or null",
  "employment_details": [
    {{"company": "...", "role": "...", "duration": "..."}}
  ],
  "technical_skills": ["skill1", "skill2"],
  "soft_skills": ["skill1", "skill2"],
  "resume_score": <integer 0-100>,
  "pass_fail": "Pass or Fail",
  "suggestions": ["improvement1", "improvement2"]
}}

Rules:
- resume_score >= 70 means pass_fail = "Pass", otherwise "Fail"
- If a field is not found, use null or an empty list
- Return ONLY the JSON object, nothing else{jd_note}"""

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": resume_data}
    ]

    # Determine provider and model
    if api_key.startswith("AIza"):
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        model_name = "gemini-1.5-flash"
    else:
        base_url = "https://openrouter.ai/api/v1"
        model_name = "meta-llama/llama-3.1-70b-instruct"

    client = OpenAI(base_url=base_url, api_key=api_key)

    last_error = None
    for attempt in range(3):
        try:
            print(f"Attempt {attempt + 1}: Calling {model_name}...")
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.0,
                max_tokens=1500,
            )

            raw_content = response.choices[0].message.content
            print(f"Raw response (first 300 chars): {raw_content[:300]}")

            parsed = _clean_and_parse_json(raw_content)
            return parsed

        except ValueError as ve:
            # JSON parsing failed — log and return helpful error
            print(f"JSON parse error on attempt {attempt + 1}: {ve}")
            last_error = str(ve)
            # Don't retry on parse errors — the model gave bad output
            return {
                "error": "The AI returned a response that could not be parsed as JSON. Try again.",
                "detail": last_error
            }

        except Exception as e:
            err_str = str(e)
            print(f"API error on attempt {attempt + 1}: {err_str}")
            if "429" in err_str and attempt < 2:
                wait = 30 * (attempt + 1)
                print(f"Rate limited. Waiting {wait}s before retry...")
                time.sleep(wait)
                last_error = err_str
            else:
                return {"error": f"AI request failed: {err_str}"}

    return {"error": f"All retry attempts failed. Last error: {last_error}"}