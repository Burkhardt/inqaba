"""JSON5 subset parser shared by configuration and ingestion."""
from typing import Any

def loads_json5(text: str) -> Any:
	"""
	Parses a JSON5 string into Python dictionaries, lists, strings, numbers, booleans, or None.
	Supports unquoted keys, single and double quotes, trailing commas, line comments (//),
	and block comments (/* ... */) without third-party dependencies.
	"""
	# Step 1: Strip comments while respecting strings
	chars = list(text)
	n = len(chars)
	i = 0
	cleaned: list[str] = []
	in_string: str | None = None
	escape = False

	while i < n:
		c = chars[i]
		if in_string:
			cleaned.append(c)
			if escape:
				escape = False
			elif c == "\\":
				escape = True
			elif c == in_string:
				in_string = None
			i += 1
		else:
			if c in ('"', "'"):
				in_string = c
				cleaned.append(c)
				i += 1
			elif c == "/" and i + 1 < n and chars[i + 1] == "/":
				# Line comment
				i += 2
				while i < n and chars[i] not in ("\r", "\n"):
					i += 1
			elif c == "/" and i + 1 < n and chars[i + 1] == "*":
				# Block comment
				i += 2
				while i + 1 < n and not (chars[i] == "*" and chars[i + 1] == "/"):
					i += 1
				i += 2
			else:
				cleaned.append(c)
				i += 1

	cleaned_str = "".join(cleaned)
	pos = 0
	length = len(cleaned_str)

	def skip_ws() -> None:
		nonlocal pos
		while pos < length and cleaned_str[pos].isspace():
			pos += 1

	def parse_value() -> Any:
		skip_ws()
		if pos >= length:
			raise ValueError("Unexpected end of JSON5 input")
		ch = cleaned_str[pos]
		if ch == "{":
			return parse_object()
		elif ch == "[":
			return parse_array()
		elif ch in ('"', "'"):
			return parse_string()
		elif ch in ("t", "f"):
			return parse_bool()
		elif ch == "n":
			return parse_null()
		else:
			return parse_number_or_ident()

	def parse_string() -> str:
		nonlocal pos
		quote = cleaned_str[pos]
		pos += 1
		res: list[str] = []
		while pos < length:
			c = cleaned_str[pos]
			if c == "\\":
				pos += 1
				if pos >= length:
					raise ValueError("Unterminated escape sequence")
				esc = cleaned_str[pos]
				if esc == "n":
					res.append("\n")
				elif esc == "r":
					res.append("\r")
				elif esc == "t":
					res.append("\t")
				elif esc == "\\":
					res.append("\\")
				elif esc == quote:
					res.append(quote)
				elif esc == "/":
					res.append("/")
				else:
					res.append(esc)
				pos += 1
			elif c == quote:
				pos += 1
				return "".join(res)
			else:
				res.append(c)
				pos += 1
		raise ValueError("Unterminated string literal")

	def parse_object() -> dict[str, Any]:
		nonlocal pos
		pos += 1  # skip {
		obj: dict[str, Any] = {}
		while True:
			skip_ws()
			if pos >= length:
				raise ValueError("Unterminated JSON5 object")
			if cleaned_str[pos] == "}":
				pos += 1
				return obj
			# Key: either quoted string or bare identifier
			if cleaned_str[pos] in ('"', "'"):
				key = parse_string()
			else:
				k_start = pos
				while pos < length and (
					cleaned_str[pos].isalnum() or cleaned_str[pos] in ("_", "$", "-")
				):
					pos += 1
				key = cleaned_str[k_start:pos]
				if not key:
					raise ValueError(f"Invalid key at position {pos}")
			skip_ws()
			if pos >= length or cleaned_str[pos] != ":":
				raise ValueError(f"Expected ':' at position {pos}")
			pos += 1  # skip :
			val = parse_value()
			obj[key] = val
			skip_ws()
			if pos < length and cleaned_str[pos] == ",":
				pos += 1
				skip_ws()
			elif pos < length and cleaned_str[pos] == "}":
				pass
			else:
				raise ValueError(f"Expected ',' or '}}' at position {pos}")

	def parse_array() -> list[Any]:
		nonlocal pos
		pos += 1  # skip [
		arr: list[Any] = []
		while True:
			skip_ws()
			if pos >= length:
				raise ValueError("Unterminated JSON5 array")
			if cleaned_str[pos] == "]":
				pos += 1
				return arr
			val = parse_value()
			arr.append(val)
			skip_ws()
			if pos < length and cleaned_str[pos] == ",":
				pos += 1
				skip_ws()
			elif pos < length and cleaned_str[pos] == "]":
				pass
			else:
				raise ValueError(f"Expected ',' or ']' at position {pos}")

	def parse_bool() -> bool:
		nonlocal pos
		if cleaned_str.startswith("true", pos):
			pos += 4
			return True
		if cleaned_str.startswith("false", pos):
			pos += 5
			return False
		raise ValueError(f"Unknown literal at position {pos}")

	def parse_null() -> None:
		nonlocal pos
		if cleaned_str.startswith("null", pos):
			pos += 4
			return None
		raise ValueError(f"Unknown literal at position {pos}")

	def parse_number_or_ident() -> Any:
		nonlocal pos
		start = pos
		if cleaned_str[pos] in ("-", "+"):
			pos += 1
		while pos < length and (
			cleaned_str[pos].isalnum() or cleaned_str[pos] in (".", "-", "+")
		):
			pos += 1
		raw = cleaned_str[start:pos]
		if not raw:
			raise ValueError(f"Invalid value at position {pos}")
		try:
			if "." in raw or "e" in raw or "E" in raw:
				return float(raw)
			if raw.startswith(("0x", "0X")):
				return int(raw, 16)
			return int(raw)
		except ValueError:
			return raw

	result = parse_value()
	skip_ws()
	if pos != length:
		raise ValueError(f"Unexpected trailing content at position {pos}")
	return result
