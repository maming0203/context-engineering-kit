"""Mini-JIT: Minimal JIT Context Assembly Engine.

A reference implementation demonstrating the two-layer
context assembly pattern for LLM prompt engineering.
"""

from .assembler import ContextAssembler, AssemblyResult
from .config import Config, INFRASTRUCTURE_SKILLS, RECIPES_DIR, SKILLS_DIR
from .loader import (
    load_recipe,
    load_skill,
    load_infrastructure_skills,
    match_recipe,
    LoadError,
)

__all__ = [
    "ContextAssembler",
    "AssemblyResult",
    "Config",
    "INFRASTRUCTURE_SKILLS",
    "RECIPES_DIR",
    "SKILLS_DIR",
    "load_recipe",
    "load_skill",
    "load_infrastructure_skills",
    "match_recipe",
    "LoadError",
]
