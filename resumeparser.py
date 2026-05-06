"""Resume parsing module using OpenRouter or Google Gemini API."""

from openai import OpenAI
import json
import re
import yaml
import os
import time
import logging

logger = logging.getLogger(__name__)

CONFIG_PATH = "config.yaml"


def _load_api_key():
    """
    Load API key from config.yaml or environment variables.
    Priority: Environment variables > config.yaml
    """
    api_key = None

    # Try environment variables first (higher priority)
    api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('OPENAI_API_KEY')
    
    if api_key and api_key.strip() not in ["", "your_api_key_here", "YOUR KEY HERE"]:
        logger.info("API key loaded from environment variables")
        return api_key

    # Fall back to config file
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as file:
                config_data = yaml.load(file, Loader=yaml.FullLoader)
                if config_data:
                    api_key = config_data.get('OPENROUTER_API_KEY') or config_data.get('OPENAI_API_KEY')
                    if api_key and api_key.strip() not in ["", "your_api_key_here", "YOUR KEY HERE"]:
                        logger.info("API key loaded from config.yaml")
                        return api_key
        except Exception as e:
            logger.warning(f"Could not read config.yaml: {e}")

    return None


def _clean_and_parse_json(raw: str) -> dict:
    """
    Robustly extract and parse JSON from model response.
    Handles markdown fences, extra text, and minor syntax errors.
    """
    if not raw or not raw.strip():
        raise ValueError("Empty response from model")

    text = raw.strip()

    # Strip markdown fences
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract first {...} block
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

        # Fix trailing commas
        fixed = re.sub(r',\s*([}\]])', r'\1', candidate)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from response:\n{raw[:300]}")


def _build_prompt(job_description: str = None) -> str:
    """Build the system prompt for resume parsing."""
    
    jd_section = ""
    if job_description:
        jd_section = f"\n\nJob Description to match against:\n{job_description}"

    prompt = f"""You are a professional resume parser and ATS analyst. Extract structured information from the resume and return ONLY a valid JSON object — no markdown, no explanation, no extra text.

The JSON must have exactly these keys:
{{
  "full_name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "github": "string or null",
  "linkedin": "string or null",
  "employment_details": [
    {{"company": "string", "role": "string", "duration": "string"}}
  ],
  "education": [
    {{"institution": "string", "degree": "string", "field": "string"}}
  ],
  "technical_skills": ["skill1", "skill2"],
  "soft_skills": ["skill1", "skill2"],
  "resume_score": <integer 0-100>,
  "pass_fail": "Pass or Fail",
  "missing_keywords": ["keyword1", "keyword2"],
  "suggestions": ["improvement1", "improvement2"]
}}

Scoring Rules:
- Format and structure: 20 points
- Contact information: 15 points
- Work experience clarity: 20 points
- Skills presentation: 20 points
- ATS compatibility: 25 points
- Pass if score >= 70, otherwise Fail

Rules:
- If a field is not found, use null or empty list
- Return ONLY the JSON object, nothing else
- employment_details and education should be empty lists if not found
- missing_keywords should highlight keywords from job description not in resume
- suggestions should be actionable improvements{jd_section}"""

    return prompt


def ats_extractor(resume_data: str, job_description: str = None) -> dict:
    """
    Extract structured ATS information from resume text using an LLM.
    
    Args:
        resume_data: Extracted text from resume
        job_description: Optional job description for matching
        
    Returns:
        Dictionary with parsed fields or error information
    """
    
    api_key = _load_api_key()

    if not api_key:
        error_msg = "API key not found. Set OPENROUTER_API_KEY or OPENAI_API_KEY in environment or config.yaml"
        logger.error(error_msg)
        return {"error": error_msg}

    # Validate resume data
    if not resume_data or not resume_data.strip():
        return {"error": "Resume text is empty"}

    # Build prompt
    system_prompt = _build_prompt(job_description)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Parse this resume:\n\n{resume_data}"}
    ]

    # Determine provider and model based on API key format
    if api_key.startswith("AIza"):
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        model_name = "gemini-1.5-flash"
        logger.info("Using Google Gemini API")
    else:
        base_url = "https://openrouter.ai/api/v1"
        model_name = "meta-llama/llama-3.1-70b-instruct"
        logger.info("Using OpenRouter API with Llama 3.1")

    client = OpenAI(base_url=base_url, api_key=api_key)

    last_error = None
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_attempts}: Calling {model_name}...")
            
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.0,
                max_tokens=1500,
            )

            raw_content = response.choices[0].message.content
            logger.debug(f"Raw response length: {len(raw_content)} chars")

            # Parse JSON response
            parsed = _clean_and_parse_json(raw_content)
            
            logger.info("Resume parsed successfully")
            return parsed

        except ValueError as ve:
            error_msg = f"JSON parsing error: {str(ve)}"
            logger.error(error_msg)
            return {
                "error": "AI returned invalid JSON. Please try again.",
                "detail": error_msg
            }

        except Exception as e:
            error_str = str(e)
            logger.warning(f"API error on attempt {attempt + 1}: {error_str}")
            last_error = error_str

            # Handle rate limiting with exponential backoff
            if "429" in error_str and attempt < max_attempts - 1:
                wait_time = 30 * (attempt + 1)
                logger.info(f"Rate limited. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue

            # Don't retry on other errors
            if attempt == max_attempts - 1:
                return {"error": f"Failed to process resume: {error_str}"}

    return {"error": f"Max retry attempts reached. Last error: {last_error}"}
