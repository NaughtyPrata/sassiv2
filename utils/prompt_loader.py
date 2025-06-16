from fastapi import HTTPException

def load_prompt(prompt_file: str) -> str:
    """Load system prompt from external markdown file"""
    try:
        with open(f"prompts/{prompt_file}", 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Prompt file not found: {prompt_file}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading prompt: {str(e)}") 