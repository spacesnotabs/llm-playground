# LLM Playground

This Python application is meant to serve as a tool to facilitate using local and remote LLMs (via APIs) to automate a variety of tasks. These include generating software applications from a simple description, writing and reviewing code, and engaging in natural conversations.

## Key Features

- **Application Building Mode:**  Takes a user's description and generates a basic file structure and code for a new application.  Very early in development so expect small apps with some bugs, but provides a decent framework. 
- **Code Mode:**  Allows users to provide instructions to modify existing code files.
- **Chat Mode:** Enables open-ended conversations with the application, leveraging the LLM's ability to understand and generate human-like text.

## Usage
In order to use APIs and local LLMs, create a `credentials.json` file in the root directory which should look similar to this:
```json
{
  "llm_apis": {
    "openai": {
      "api_key": "123-456-7890",
      "org_id": ""
    },
    "anthropic": {
      "api_key": "sk-abcdefghijklmnop"
    },
    "gemini": {
      "api_key": "Ba398Fj390Jlakj"
    },
    "mistral": {
      "model_dir": "C:\\Users\\UserName\\models\\mistral_models\\Mistral-7B-Instruct-v0.3-GGUF",
      "model_file": "Mistral-7B-Instruct-v0.3.Q4_K_M.gguf"
    }
  },

```
To run the web application, simply run the following
  ```bash
  python app.py
  ```

The CLI verion of the application offers three distinct modes of operation:

- **Build App Mode:**  
  ```bash
  python llm.py --mode build_app_mode
  ```

- **Code Mode:**
  ```bash
  python llm.py --mode code_mode
  ```

- **Chat Mode:**
  ```bash
  python llm.py --mode chat_mode
  ```

## Future Improvements

- Integrate with additional LLM providers and models to expand capabilities and offer more choices.
- Enhance the user interface for a more intuitive and user-friendly experience.
- Develop new agent types and functionalities to further broaden the application's skillset.
- Improve error handling and overall system robustness for a smoother user experience.

