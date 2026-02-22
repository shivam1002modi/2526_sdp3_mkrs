import os
import re
import subprocess
import json
import time

ACTIONS_PATH = r"d:\MKRS\ai-service\actions\actions.py"
EVAL_PATH = r"d:\MKRS\ai-service\eval_v1.py"
PYTHON_PATH = r"d:\MKRS\ai-service\venv\Scripts\python.exe"

def update_actions_config(k, top_n, num_predict, temp, repeat_penalty):
    with open(ACTIONS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update k (Line 233)
    content = re.sub(r'k=\d+\)', f'k={k})', content)
    
    # Update num_predict (generation options only - usually follows top_p or temperature)
    content = re.sub(r'"num_predict": \d+,\s+"repeat_penalty"', f'"num_predict": {num_predict},\n                        "repeat_penalty"', content)
    # If the above fails due to formatting, try a more direct approach at line indices if possible, 
    # but re.sub with context is better.
    
    # Update temperature
    content = re.sub(r'"temperature": \d+\.\d+,', f'"temperature": {temp},', content)
    
    # Update repeat_penalty
    content = re.sub(r'"repeat_penalty": \d+\.\d+,', f'"repeat_penalty": {repeat_penalty},', content)
    
    # Update top-N (context chunks - Line 265)
    content = re.sub(r'scored_docs\[:\d+\]\): # top-\d+', f'scored_docs[:{top_n}]): # top-{top_n}', content)

    # Add keep_alive to the generation payload if not present
    if '"keep_alive": "10m"' not in content:
        # Specifically targeting the generation call which has timeout=OLLAMA_TIMEOUT
        content = content.replace('"stream": False,\n                    "options": {', '"stream": False,\n                    "keep_alive": "10m",\n                    "options": {')

    with open(ACTIONS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

def run_benchmark(test_name):
    cmd = [PYTHON_PATH, EVAL_PATH, "--name", test_name]
    print(f"Running benchmark: {test_name}...")
    subprocess.run(cmd, check=True)

def get_latest_score():
    mbs_dir = r"d:\MKRS\MBS"
    subdirs = [os.path.join(mbs_dir, d) for d in os.listdir(mbs_dir) if os.path.isdir(os.path.join(mbs_dir, d)) and d.startswith("TEST_")]
    latest_dir = max(subdirs, key=os.path.getmtime)
    raw_scores_path = os.path.join(latest_dir, "raw_scores.json")
    
    if os.path.exists(raw_scores_path):
        with open(raw_scores_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("tms_score", 0), data.get("breakdown", {})
    return 0, {}

# Define configs to test
# Format: (k, top_n, num_predict, temp, repeat_penalty)
configs = [
    (10, 3, 300, 0.0, 1.1),  # Near peak (T09) but zero temp
    (10, 3, 300, 0.1, 1.1),
    (15, 3, 300, 0.05, 1.1),
    (15, 4, 300, 0.05, 1.1),
    (10, 3, 200, 0.05, 1.1), # Fast version
]

results = []

for config in configs:
    k, top_n, num_predict, temp, repeat_penalty = config
    test_name = f"TUNER_k{k}_n{top_n}_p{num_predict}_t{temp}_rp{repeat_penalty}"
    
    update_actions_config(k, top_n, num_predict, temp, repeat_penalty)
    time.sleep(2) # Give OS a breath
    
    try:
        run_benchmark(test_name)
        score, breakdown = get_latest_score()
        results.append({
            "config": config,
            "score": score,
            "breakdown": breakdown
        })
        print(f"Result for {test_name}: TMS = {score}")
    except Exception as e:
        print(f"Error running {test_name}: {e}")

# Save all tuner results
with open(r"d:\MKRS\MBS\tuner_results.json", 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4)

best = max(results, key=lambda x: x["score"])
print(f"\nOptimization Complete!")
print(f"Best config: {best['config']}")
print(f"Best score: {best['score']}")
