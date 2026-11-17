import json
from collections import defaultdict

with open("packages/tool-registry/tools.json", "r", encoding="utf-8") as f:
    tools = json.load(f)

categories = defaultdict(list)
for t in tools:
    categories[t["category"]].append((t["number"], t["name"], t["operation"]))

for cat, tool_list in sorted(categories.items()):
    print(f"=== {cat} ({len(tool_list)} tools) ===")
    for num, name, op in tool_list[:8]:
        print(f"  #{num:03d}: {name} ({op})")
    if len(tool_list) > 8:
        print(f"  ... and {len(tool_list) - 8} more")
    print()
