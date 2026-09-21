import json
from pathlib import Path
import re
import subprocess

from tree_sitter import Language, Parser, Query
import tree_sitter_java as tsjava
from tree_sitter import QueryCursor

JAVA_LANGUAGE = Language(tsjava.language())
parser = Parser(JAVA_LANGUAGE)

search_query = Query(JAVA_LANGUAGE, """
    (method_invocation
      name: (identifier) @method_name)
""")
cursor = QueryCursor(search_query)

def get_call_references(method_name,case_sensitive: bool=False):
	base_path = Path('./fixture-repo/')
	flags = 0 if case_sensitive else re.IGNORECASE
	compiled_pattern = re.compile(re.escape(method_name), flags)
	java_files = list(base_path.rglob("*.java"))
	matches = []
	for java_file in java_files:
		result = search_partial_keyword_in_file(java_file, compiled_pattern)
		if(result):
			matches = matches+result
	print(matches)
	return matches

def search_partial_keyword_in_file(java_file,pattern):
	try:
		source_bytes = java_file.read_bytes()
		tree = parser.parse(source_bytes)
		captures = cursor.captures(tree.root_node)
		matches = []
		for capture_name, nodes in captures.items():
			for node in nodes:
				name_text = source_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
				if pattern.search(name_text):
					line_number = node.start_point[0] + 1
					source_text = source_bytes.decode('utf-8', errors='ignore')
					lines = source_text.splitlines()
					line_snippet = lines[line_number - 1].strip()
					matches.append({"line": line_number, "file": str(java_file), "snippet": line_snippet})

		return matches

	except Exception as e:
		print(f"❌ Error reading {java_file}: {e}")
		return None

def get_keyword_result(keyword):
	result = subprocess.run(
		["rg",keyword, "./fixture-repo/", "--json"],
		capture_output=True,
		text=True
	)

	matches = []

	for line in result.stdout.splitlines():
		obj = json.loads(line)

		if obj["type"] == "match":
			data = obj["data"]

			matches.append({
				"file": data["path"]["text"],
				"line": data["line_number"],
				"snippet": data["lines"]["text"].rstrip()
			})

	print(matches)
	return matches


