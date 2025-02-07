# LLM Playground

This Python application leverages LLMs to automate system operations and development tasks. While several features are under development, the Linux operator functionality is more thoroughly tested and fun to use!  I do recommend doing it in a virtual Linux environment.

## Key Features

- **Linux Operator (Production Ready):** Automates Linux system operations through natural language commands, leveraging LLMs to interpret instructions and execute appropriate system commands.
- **Application Building Mode (In Development):** Takes a user's description and generates basic application scaffolding.
- **Code Mode (In Development):** Assists with code modifications and reviews.
- **Chat Mode (In Development):** Enables general-purpose LLM interactions.

## Usage

### Setup
1. Create a `credentials.json` file in the `credentials` directory:
```json
{
  "llms": {
    "openai": {
      "api_key": "your-api-key-here",
      "org_id": ""
    },
    "anthropic": {
      "api_key": "your-anthropic-key"
    }
  }
}
```

2. Run the Linux operator:
```bash
usage: run_linux_op.py [-h] [-t TASK] [-i]

Linux Operation Assistant

options:
  -h, --help            show this help message and exit
  -t TASK, --task TASK  Linux task to execute
  -i, --interactive     Run in interactive mode
```

The Linux operator accepts natural language instructions like:
- "Find all Python files modified in the last 24 hours"
- "Show me the disk usage in the current directory"
- "List all processes using more than 1GB of memory"

### Other Modes (In Development)
Additional functionality is available but still under development:

```bash
python llm.py --mode build_app_mode  # Application generation
python llm.py --mode code_mode       # Code modification
python llm.py --mode chat_mode       # General conversation
```

A prototype web interface is also available (early development stage):
```bash
python app.py
```

## Future Improvements

- Expand Linux operator capabilities with more sophisticated command patterns
- Add support for automated system maintenance tasks
- Develop safety frameworks for system operations
- Complete development of application building and code modification features
- Enhance the web interface with full Linux operator support

