"""Generate a reviewable class inventory from source without importing it.

Usage: python scripts/class_diagram.py PACKAGE OUTPUT.puml
Render the result with plantuml -tsvg OUTPUT.puml.
"""
import ast
from pathlib import Path
import sys


def main():
	package, output = map(Path, sys.argv[1:])
	classes = []
	for source in sorted(package.glob("*.py")):
		for node in ast.parse(source.read_text()).body:
			if isinstance(node, ast.ClassDef):
				classes.append((source.stem, node))
	known = {node.name for _, node in classes}
	lines = ["@startuml", "skinparam classAttributeIconSize 0", "hide empty members", "left to right direction"]
	for module in sorted({module for module, _ in classes}):
		lines.append(f'package "{package.name}.{module}" {{')
		for owner, node in classes:
			if owner != module: continue
			lines.append(f"class {node.name} {{")
			for member in node.body:
				if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
					if member.name.startswith("_") and member.name != "__init__": continue
					params = ", ".join(a.arg for a in member.args.args if a.arg not in ("self", "cls"))
					lines.append(f"  + {member.name}({params})")
				elif isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name):
					lines.append(f"  {member.target.id}")
			lines.append("}")
		lines.append("}")
	for _, node in classes:
		for base in node.bases:
			base = base.value if isinstance(base, ast.Subscript) else base
			if isinstance(base, ast.Name) and base.id in known:
				lines.append(f"{node.name} --|> {base.id}")
	if package.name == "inqaba":
		lines.extend(["InqFile --> InqPath : parent", "InqPath ..> InqRelPath : anchors", "InqConfig --> InqPath : configured roots", 'InqEntry *-- "pathlib.Path" : embedded'])
	else:
		lines.extend(["Pit o-- PitItem : live slots", "Pit --> PitItems : history", "Pit --> ChangeFile", "Pit --> ReceiptFile", "JsonPitBase --> ProcessFlagFile", "JsonPitBase --> MasterFlagFile", 'JsonPitBase --> "inqaba.InqConfig"', 'JsonPitBase --> "inqaba.InqPath" : pit_dir', 'ChangeFile --> "inqaba.InqFile"', "PitAudit --> PitAuditReadResult", "PitAuditReadResult o-- PitAuditEvent"])
	lines.append("@enduml")
	output.write_text("\n".join(lines) + "\n")


if __name__ == "__main__": main()
