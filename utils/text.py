import re

def clean_input(text: str) -> str:
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip().lower()