import re
import subprocess
import json
import time
import os

ACTIONS_PATH = r"d:\MKRS\ai-service\actions\actions.py"
EVAL_PATH = r"d:\MKRS\ai-service\eval_v1.py"
PYTHON_PATH = r"d:\MKRS\ai-service\venv\Scripts\python.exe"

def update_super_config(k, top_n, num_predict, temp, repeat_penalty):
    with open(ACTIONS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update k
    content = re.sub(r'k=\d+\)', f'k={k})', content)
    
    # Update num_predict and temp
    content = re.sub(r'"num_predict": \d+,\s+"repeat_penalty"', f'"num_predict": {num_predict},\n                        "repeat_penalty"', content)
    content = re.sub(r'"temperature": \d+\.\d+,', f'"temperature": {temp},', content)
    content = re.sub(r'"repeat_penalty": \d+\.\d+,', f'"repeat_penalty": {repeat_penalty},', content)
    
    # Update top-N
    content = re.sub(r'scored_docs\[:\d+\]\): # top-\d+', f'scored_docs[:{top_n} ]): # top-{top_n}', content)

    # UPDATED PROMPT - No preamble, focus on density of facts
    new_prompt_body = (
        "You are a document assistant that answers questions by DIRECTLY QUOTING "
        "from the provided context documents.\n\n"
        "RULES:\n"
        "1. NO PREAMBLE. Do NOT say 'Based on the context' or 'The document states'. Start the answer immediately.\n"
        "2. QUOTE VERBATIM. Use the EXACT words, names, dates, and numbers. Do NOT paraphrase.\n"
        "3. Include ALL technical details provided (like specific chemicals, years, and city names).\n"
        "4. Only use facts from the document relevant to the question.\n"
        "5. If the answer is not present, say exactly: 'The documents do not contain this information.'\n"
        "6. Max 3 sentences. Focus only on the direct answer.\n\n"
        f"CONTEXT:\n{{context}}\n\n"
        f"QUESTION: {{question}}\n\n"
        "ANSWER (verbatim quote, no preamble):"
    )
    
    # Surgical replacement of the prompt string
    content = re.sub(r'prompt = \((.*?)\)\n\n        try:', f'prompt = ("{new_prompt_body}")\n\n        try:', content, flags=re.DOTALL)

    with open(ACTIONS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

# The "Super Config" targeting 72+
config = (12, 3, 350, 0.12, 1.05)
k, top_n, num_predict, temp, rp = config

update_super_config(k, top_n, num_predict, temp, rp)
subprocess.run([PYTHON_PATH, EVAL_PATH, "--name", "SUPER_CONFIG_V2_72PLUS_TARGET"], check=True)
