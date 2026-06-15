#!/usr/bin/env python3
"""
Context Engineering Kit — Validation Script

Validates recipe JSON files, SKILL.md files, and infrastructure config files.
"""

import json
import sys
import os
import re
import argparse
from pathlib import Path
from typing import List, Tuple


def validate_recipe(recipe_path: str) -> Tuple[bool, List[str]]:
  """Validate a recipe JSON file against the expected schema."""
  errors = []

  if not os.path.exists(recipe_path):
    return False, [f"File not found: {recipe_path}"]

  try:
    with open(recipe_path, "r", encoding="utf-8") as f:
      data = json.load(f)
  except json.JSONDecodeError as e:
    return False, [f"Invalid JSON: {e}"]

  # Required fields
  required_fields = ["name", "version", "description", "trigger_keywords", "skills", "constraints", "output_format"]
  for field in required_fields:
    if field not in data:
      errors.append(f"Missing required field: '{field}'")

  # Validate trigger_keywords
  if "trigger_keywords" in data:
    if not isinstance(data["trigger_keywords"], list):
      errors.append("'trigger_keywords' must be an array")
    elif len(data["trigger_keywords"]) == 0:
      errors.append("'trigger_keywords' must not be empty")

  # Validate skills
  if "skills" in data:
    if not isinstance(data["skills"], list):
      errors.append("'skills' must be an array")
    elif len(data["skills"]) == 0:
      errors.append("'skills' must not be empty")

  # Validate constraints
  if "constraints" in data:
    constraints = data["constraints"]
    if not isinstance(constraints, dict):
      errors.append("'constraints' must be an object")
    else:
      if "max_tokens" in constraints and not isinstance(constraints["max_tokens"], (int, float)):
        errors.append("'constraints.max_tokens' must be a number")
      if "max_steps" in constraints and not isinstance(constraints["max_steps"], (int, float)):
        errors.append("'constraints.max_steps' must be a number")

  # Validate output_format
  if "output_format" in data:
    output_format = data["output_format"]
    if not isinstance(output_format, dict):
      errors.append("'output_format' must be an object")
    else:
      if "type" not in output_format:
        errors.append("'output_format.type' is required")
      if "format" not in output_format:
        errors.append("'output_format.format' is required")

  # Validate version format (semver-like)
  if "version" in data:
    if not re.match(r"^\d+\.\d+\.\d+$", str(data["version"])):
      errors.append(f"'version' should follow semver format (e.g., 1.0.0), got: {data['version']}")

  return len(errors) == 0, errors


def validate_skill(skill_path: str) -> Tuple[bool, List[str]]:
  """Validate a SKILL.md file for format and size constraints."""
  errors = []

  if not os.path.exists(skill_path):
    return False, [f"File not found: {skill_path}"]

  # Check file size (must be < 4KB)
  file_size = os.path.getsize(skill_path)
  if file_size >= 4096:
    errors.append(f"File size is {file_size} bytes, must be under 4096 bytes (4KB)")

  with open(skill_path, "r", encoding="utf-8") as f:
    content = f.read()

  # Check YAML Frontmatter
  if not content.startswith("---"):
    errors.append("Missing YAML Frontmatter (file must start with '---')")
  else:
    # Find closing ---
    parts = content.split("---", 2)
    if len(parts) < 3:
      errors.append("YAML Frontmatter is not properly closed (missing second '---')")
    else:
      frontmatter = parts[1].strip()
      # Check required frontmatter fields
      required_fm = ["name", "version", "description"]
      for field in required_fm:
        if not re.search(rf"^{field}:", frontmatter, re.MULTILINE):
          errors.append(f"Missing required frontmatter field: '{field}'")

  # Check required sections
  required_sections = ["When to Use", "Steps", "Pitfalls", "Verification"]
  for section in required_sections:
    if f"## {section}" not in content:
      errors.append(f"Missing required section: '## {section}'")

  return len(errors) == 0, errors


def validate_infrastructure(config_path: str) -> Tuple[bool, List[str]]:
  """Validate an infrastructure configuration JSON file."""
  errors = []

  if not os.path.exists(config_path):
    return False, [f"File not found: {config_path}"]

  try:
    with open(config_path, "r", encoding="utf-8") as f:
      data = json.load(f)
  except json.JSONDecodeError as e:
    return False, [f"Invalid JSON: {e}"]

  # Required fields
  if "version" not in data:
    errors.append("Missing required field: 'version'")

  if "description" not in data:
    errors.append("Missing required field: 'description'")

  if "skills" not in data:
    errors.append("Missing required field: 'skills'")
  else:
    if not isinstance(data["skills"], list):
      errors.append("'skills' must be an array")
    else:
      for i, skill in enumerate(data["skills"]):
        if not isinstance(skill, dict):
          errors.append(f"skills[{i}] must be an object")
          continue
        if "name" not in skill:
          errors.append(f"skills[{i}] missing 'name' field")
        if "reason" not in skill:
          errors.append(f"skills[{i}] missing 'reason' field")

  return len(errors) == 0, errors


def main():
  parser = argparse.ArgumentParser(
    description="Validate Context Engineering Kit files (recipes, skills, infrastructure configs)."
  )
  parser.add_argument(
    "files",
    nargs="*",
    help="Files to validate. Supports: *.json (recipe/infrastructure), SKILL.md"
  )
  parser.add_argument(
    "--type",
    choices=["recipe", "skill", "infrastructure", "auto"],
    default="auto",
    help="File type to validate (default: auto-detect)"
  )
  parser.add_argument(
    "--dir",
    help="Recursively validate all matching files in a directory"
  )

  args = parser.parse_args()

  if not args.files and not args.dir:
    parser.error("At least one of 'files' or '--dir' is required")

  files_to_validate = []

  if args.dir:
    dir_path = Path(args.dir)
    if not dir_path.is_dir():
      print(f"Error: {args.dir} is not a directory", file=sys.stderr)
      sys.exit(1)
    for f in dir_path.rglob("*"):
      if f.is_file():
        files_to_validate.append(str(f))
  else:
    files_to_validate = args.files

  total = 0
  passed = 0
  failed = 0

  for file_path in files_to_validate:
    file_type = args.type

    # Auto-detect file type
    if file_type == "auto":
      basename = os.path.basename(file_path)
      if basename == "SKILL.md":
        file_type = "skill"
      elif "infrastructure" in basename.lower():
        file_type = "infrastructure"
      elif file_path.endswith(".json"):
        file_type = "recipe"
      else:
        print(f"  SKIP  {file_path} (cannot auto-detect type, use --type)")
        continue

    total += 1
    rel_path = os.path.relpath(file_path)

    if file_type == "recipe":
      ok, errors = validate_recipe(file_path)
    elif file_type == "skill":
      ok, errors = validate_skill(file_path)
    elif file_type == "infrastructure":
      ok, errors = validate_infrastructure(file_path)
    else:
      print(f"  SKIP  {rel_path} (unknown type)")
      continue

    if ok:
      passed += 1
      print(f"  PASS  {rel_path}")
    else:
      failed += 1
      print(f"  FAIL  {rel_path}")
      for err in errors:
        print(f"        - {err}")

  print(f"\n{'='*50}")
  print(f"Total: {total} | Passed: {passed} | Failed: {failed}")

  if failed > 0:
    sys.exit(1)
  else:
    print("All validations passed! ✓")
    sys.exit(0)


if __name__ == "__main__":
  main()
