import json

with open("packages/tool-registry/tools.json", "r", encoding="utf-8") as f:
    tools = json.load(f)

for num in [33, 34, 35, 36, 46, 47, 102, 116, 147, 441]:
    t = next(x for x in tools if x["number"] == num)
    print(f"#{t['number']:03d} {t['name']}:")
    print(f"   \"{t['description']}\"\n")
