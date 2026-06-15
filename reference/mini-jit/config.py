"""Mini-JIT Configuration — paths and skill registry."""

from pathlib import Path
from typing import List

# Base directory for this package
BASE_DIR = Path(__file__).resolve().parent

# Directory containing recipe JSON files
RECIPES_DIR: Path = BASE_DIR / "recipes"

# Directory containing skill markdown files
SKILLS_DIR: Path = BASE_DIR / "skills"

# Infrastructure skills loaded unconditionally on every request
INFRASTRUCTURE_SKILLS: List[str] = [
    "core_reasoning",
    "output_formatting",
    "safety_guardrails",
]


class Config:
    """Simple configuration container."""

    def __init__(
        self,
        recipes_dir: Path = RECIPES_DIR,
        skills_dir: Path = SKILLS_DIR,
        infrastructure_skills: List[str] = None,
    ):
        self.recipes_dir = recipes_dir
        self.skills_dir = skills_dir
        self.infrastructure_skills = infrastructure_skills or list(INFRASTRUCTURE_SKILLS)
