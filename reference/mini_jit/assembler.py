"""Mini-JIT Assembler — two-layer context assembly engine."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .config import Config
from .loader import (
    load_infrastructure_skills,
    load_recipe,
    load_skill,
    match_recipe,
    LoadError,
)


@dataclass
class AssemblyResult:
    """Result of a context assembly operation."""

    prompt: str = ""
    infrastructure_skills: List[str] = field(default_factory=list)
    recipe_name: Optional[str] = None
    task_skills: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class ContextAssembler:
    """Two-layer JIT context assembly engine.

    L0 (Infrastructure): Always loaded — core reasoning, formatting, safety.
    L1 (Task): Loaded on-demand based on recipe matching.
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()

    def assemble(self, user_input: str) -> AssemblyResult:
        """Assemble context for a given user input.

        Steps:
            1. Load all infrastructure skills (unconditional).
            2. Match user input to a recipe via trigger words.
            3. If matched, load the recipe's task skills.
            4. Build and return the final prompt.

        Args:
            user_input: Raw user input text.

        Returns:
            AssemblyResult with assembled prompt and metadata.
        """
        result = AssemblyResult()

        # Layer 1: Infrastructure (always loaded)
        infra_contents = load_infrastructure_skills(self.config)
        result.infrastructure_skills = infra_contents

        # Layer 2: Task-specific (on-demand)
        recipe_name = match_recipe(user_input, self.config)
        if recipe_name:
            result.recipe_name = recipe_name
            try:
                recipe = load_recipe(recipe_name, self.config)
                task_skill_names = recipe.get("skills", [])
                for skill_name in task_skill_names:
                    try:
                        result.task_skills.append(load_skill(skill_name, self.config))
                    except LoadError as e:
                        result.errors.append(str(e))
            except LoadError as e:
                result.errors.append(str(e))

        # Build final prompt
        all_parts = result.infrastructure_skills + result.task_skills
        result.prompt = self.build_prompt(all_parts, user_input)

        return result

    def build_prompt(self, context_parts: List[str], user_input: str) -> str:
        """Build the final prompt from context parts and user input.

        Args:
            context_parts: List of skill/recipe content strings.
            user_input: The user's raw input.

        Returns:
            Assembled prompt string.
        """
        sections = []

        if context_parts:
            sections.append("## System Context")
            for i, part in enumerate(context_parts, 1):
                sections.append(f"### Skill {i}\n{part}")

        sections.append("## User Request")
        sections.append(user_input)

        return "\n\n".join(sections)
