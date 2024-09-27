import json
import re
import yaml


def json_from_str(input: str) -> (bool, dict):
    """
    Attempts to parse a string as JSON.

    Args:
        input (str): The string to parse.

    Returns:
        tuple: A tuple containing a boolean indicating success and the parsed JSON object if successful,
               otherwise an empty dictionary.
    """
    ret = True
    output = {}
    try:
        output = json.loads(input)
    except Exception as e:
        ret = False
    finally:
        return ret, output


def extract_json(string) -> dict:
    """
    Extracts the first JSON object from a string.

    Args:
        string (str): The string to extract JSON from.

    Returns:
        dict: The extracted JSON object, or None if no valid JSON object is found.
    """
    # Find the index of the first '{'
    start = string.find('{')
    if start == -1:
        return None  # No JSON object found

    # Initialize the bracket counter and end position
    bracket_count = 0
    end = start

    # Iterate through the string starting from the first '{'
    for i in range(start, len(string)):
        if string[i] == '{':
            bracket_count += 1
        elif string[i] == '}':
            bracket_count -= 1

        # If bracket_count is 0, we've found the end of the JSON object
        if bracket_count == 0:
            end = i + 1
            break

    # Extract the JSON substring
    json_str = string[start:end]

    # Attempt to parse the extracted string as JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return json_str  # Return the raw string if it's not valid JSON


def extract_content(text) -> str | None:
    """
    Extracts the content between opening and closing delimiters.

    Args:
        text (str): The text to search in.

    Returns:
        str: The content between the delimiters, or None if not found.
    """
    code_str = None
    summary_str = None

    # Match triple backtick blocks with or without language specifier
    backtick_pattern = r'(?m)^\s*```(\w+)?\s*(.*?)^```'
    backtick_match = re.findall(backtick_pattern, text, re.DOTALL)
    if backtick_match:
        code_str = backtick_match[0][1]
    else:
        code_str = text

    return code_str

def load_prompt(yaml_file: str, prompt_name: str):
    with open(yaml_file, 'r') as file:
        prompts = yaml.safe_load(file)

    prompt_data = prompts['prompts'].get(prompt_name, {})

    # Define the order of fields and their corresponding tags
    field_order = [
        ('instruction', 'instruction'),
        ('output_format', 'output_format'),
        ('additional_instructions', 'additional_instructions'),
        ('example_output', 'example'),
        ('final_instruction', 'final_instruction')
    ]

    prompt_parts = []
    for field, tag in field_order:
        if field in prompt_data:
            content = prompt_data[field].strip()
            prompt_parts.append(f"<{tag}> {content} </{tag}>")

    return " ".join(prompt_parts)
