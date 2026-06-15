"""Mini-JIT Loader — loads recipes and skills from disk."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import Config, RECIPES_DIR, SKILLS_DIR, INFRASTRUCTURE_SKILLS


class LoadError(Exception):
    """Raised when a recipe or skill cannot be loaded."""


def load_recipe(recipe_name: str, config: Optional[Config] = None) -> Dict[str, Any]:
    """Load a recipe JSON file by name.

    Args:
        recipe_name: Name of the recipe (without .json extension).
        config: Optional config override.

    Returns:
        Parsed recipe dictionary.

    Raises:
        LoadError: If file not found or JSON is malformed.
    """
    cfg = config or Config()
    path = cfg.recipes_dir / f"{recipe_name}.json"
    if not path.exists():
        raise LoadError(f"Recipe not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise LoadError(f"Malformed JSON in {path}: {e}")


def load_skill(skill_name: str, config: Optional[Config] = None) -> str:
    """Load a SKILL.md file by name.

    Args:
        skill_name: Name of the skill directory/file.
        config: Optional config override.

    Returns:
        Skill content as string.

    Raises:
        LoadError: If file not found.
    """
    cfg = config or Config()
    # Support both skill_name/SKILL.md and skill_name.md
    candidates = [
        cfg.skills_dir / skill_name / "SKILL.md",
        cfg.skills_dir / f"{skill_name}.md",
    ]
    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8")
    raise LoadError(f"Skill not found: {skill_name} (looked in {candidates})")


def load_infrastructure_skills(config: Optional[Config] = None) -> List[str]:
    """Load all infrastructure-layer skills.

    Returns:
        List of skill content strings.
    """
    cfg = config or Config()
    contents = []
    for name in cfg.infrastructure_skills:
        try:
            contents.append(load_skill(name, cfg))
        except LoadError:
            # Infrastructure skills should exist; skip with warning in prod
            pass
    return contents


def match_recipe(user_input: str, config: Optional[Config] = None) -> Optional[str]:
    """Match user input against recipe trigger words.

    Scans all recipe files and returns the first recipe whose
    'triggers' list has any word found in user_input.

    Args:
        user_input: The user's raw input text.
        config: Optional config override.

    Returns:
        Recipe name if matched, else None.
    """
    cfg = config or Config()
    if not cfg.recipes_dir.exists():
        return None

    input_lower = user_input.lower()
    for recipe_path in sorted(cfg.recipes_dir.glob("*.json")):
        try:
            recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        triggers = recipe.get("triggers", [])
        if any(trigger.lower() in input_lower for trigger in triggers):
            return recipe_path.stem
    return None
