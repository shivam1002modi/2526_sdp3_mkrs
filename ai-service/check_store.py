
import json
import os

store_path = r"d:\MKRS\ai-service\documents\parent_store.json"
if os.path.exists(store_path):
    with open(store_path, "r", encoding="utf-8") as f:
        store = json.load(f)
    
    for pid, content in store.items():
        if "stress_test.pdf" in content or "Jezero" in content or "hydrogen" in content:
            print(f"ID: {pid}")
            print(f"Content: {content}")
            print("-" * 50)
else:
    print("Store not found")
