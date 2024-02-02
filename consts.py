CONFIG_FILE="config.yml"
MODEL_DIR="models"

LANGS = ['Python', "JavaScript", "TypeScript", "Java", "C", "CPP", "C-Sharp", "Go", "Ruby", "Rust", "Markdown",
         "Shell", "R", "SQL", "HTML", "Makefile", "PHP"]

INITIAL_PROMPT = """You are an AI programming assistant generating code based on users' programming tasks. You refuse other type of instructions.
### Instruction:
Generate {language} code for {task}
### Response:"""

MODIFY_PROMPT = """You are an AI programming assistant generating code based on users' programming tasks. You refuse other type of instructions.
### Instruction:
I have a task and there's an initial {language} code for it.
Task:
{task}
Code:
```
{code}
```
I want you to modify the code based on my request: 
{msg}
### Response:"""
