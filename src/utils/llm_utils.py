import os
from typing import List,Dict, Any
import re
import json
import requests
from dotenv import load_dotenv

from ..logger import logger
load_dotenv()

# LLM API configuration
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

def extract_response_from_llm(response, possible_moves=None, schema=None):
    """Extract the response from the LLM based on schema or fallback to move extraction"""
    try:
        if not response or "choices" not in response:
            return None

        content = response["choices"][0]["message"]["content"]
        logger.debug(f"LLM response: {content}")

        # If schema is provided, try to parse as JSON first
        if schema:
            return extract_with_schema(content, schema, possible_moves)
        else:
            return content.strip()
                
    except Exception as e:
        logger.error(f"Error extracting response: {e}")
        return None


def extract_with_schema(content: str, schema: Dict[str, Any], possible_moves=None):
    """Extract response using provided schema"""
    try:
        # Try to find JSON in the response - look for JSON inside code blocks first
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
            r'```\s*(\{.*?\})\s*```',      # JSON in generic code blocks  
            r'(\{.*?\})'                    # Standalone JSON
        ]
        
        parsed_response = None
        for pattern in json_patterns:
            json_match = re.search(pattern, content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)  # Get the captured group
                logger.debug(f"Extracted JSON string: {json_str[:100]}...")
                try:
                    parsed_response = json.loads(json_str)
                    logger.debug(f"Successfully parsed JSON: {parsed_response}")
                    break
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON with pattern {pattern}: {e}")
                    continue
        
        if parsed_response:
            if validate_schema_response(parsed_response, schema):                
                return parsed_response
            else:
                logger.warning("Response doesn't match expected schema structure")
        
        # If JSON parsing failed, try to extract values using schema field names
        logger.debug("JSON parsing failed, trying text extraction")
        return extract_fields_from_text(content, schema, possible_moves)
        
    except Exception as e:
        logger.error(f"Error in schema extraction: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def validate_schema_response(response: Dict, schema: Dict) -> bool:
    """Validate that response contains expected fields from schema"""
    schema_keys = set(schema.keys())
    response_keys = set(response.keys())
    
    # Check if at least some of the expected fields are present
    return len(schema_keys.intersection(response_keys)) > 0


def extract_fields_from_text(content: str, schema: Dict, possible_moves=None) -> Dict:
    """Extract fields from text when JSON parsing fails"""
    result = {}
    
    for field_name, field_type in schema.items():
        # Look for field name in content
        patterns = [
            f"{field_name}:\\s*(.+?)(?:\\n|$)",
            f"{field_name.replace('_', ' ')}:\\s*(.+?)(?:\\n|$)",
            f"{field_name.upper()}:\\s*(.+?)(?:\\n|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Clean up the value
                for char in [".", ",", ":", ";", '"', "'"]:
                    value = value.replace(char, "")
                value = value.strip()
                
                result[field_name] = value
                break
    
    return result if result else None


def consult_llm(board_repr: str, prompt: str, system_prompt: str,
                possible_moves: List = [], hints: List = [],
                best_move: str = '', schema: Dict[str, Any] = None, **prompt_params):
    """Send game state to LLM and get response based on schema or move recommendation
    
    Args:
        board_repr: String representation of the board
        prompt: The prompt template to send to LLM
        system_prompt: Optional system prompt
        possible_moves: List of possible moves (can be strings or dicts with 'move' key)
        hints: List of hints
        best_move: Best move if known
        schema: Optional schema defining expected response format
        **prompt_params: Additional parameters to inject into the prompt
    """
    try:
        if not prompt:
            logger.error("Prompt is required for LLM consultation.")
            return None

        prompt_params = {
            "board_repr": board_repr,
            "possible_moves": possible_moves,
            "hints": hints,
            "best_move": best_move,
            "schema": json.dumps(schema, indent=2),
            **prompt_params
        }
        
        formatted_prompt = prompt.format(**prompt_params)
        
        llm_response = call_openai_api(formatted_prompt, system_prompt=system_prompt)

        # Extract response using schema or fallback to move extraction
        result = extract_response_from_llm(llm_response, possible_moves, schema)

        if result:
            logger.debug(f"LLM response extracted: {result}")
            return result
        logger.warning("LLM did not provide a valid response.")
        return None
        
    except Exception as e:
        logger.error(f"Error consulting LLM: {e}")
        import traceback
        logger.error(traceback.format_exc())
        logger.warning("LLM did not provide a valid response.")
        return None


def call_openai_api(prompt:str, system_prompt:str):
    """Call the OpenAI API"""
    try:
        base_url = os.getenv("LLM_API_URL")
        deployment = "gpt-4o"
        api_key = os.getenv("LLM_API_KEY")
        url = f"{base_url}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        data = {
            "model": deployment,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 8000,
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error calling API: {e}")
        return None


