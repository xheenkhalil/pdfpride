import json

with open("packages/tool-registry/tools.json", "r", encoding="utf-8") as f:
    tools = json.load(f)

print(f"Total tools: {len(tools)}\n")
for t in tools[:20]:
    print(f"#{t['number']:03d} {t['name']}:")
    print(f"   \"{t['description']}\"\n")
