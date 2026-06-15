#!/usr/bin/env python3
"""Quick demo of the Mini-JIT context assembly engine."""

import sys
from pathlib import Path

# Add parent directory to path for import
sys.path.insert(0, str(Path(__file__).parent.parent))

from mini_jit import ContextAssembler


def main():
    """Run a simple demo."""
    print("Mini-JIT Demo")
    print("=" * 60)
    
    assembler = ContextAssembler()
    
    # Test case 1: Generic input (no recipe match)
    print("\n[Test 1] Generic input")
    print("-" * 60)
    user_input = "What's the weather like today?"
    result = assembler.assemble(user_input)
    print(f"Input: {user_input}")
    print(f"Recipe matched: {result.recipe_name or 'None'}")
    print(f"Infrastructure skills loaded: {len(result.infrastructure_skills)}")
    print(f"Task skills loaded: {len(result.task_skills)}")
    print(f"Total prompt length: {len(result.prompt)} chars")
    
    # Test case 2: Recipe match
    print("\n[Test 2] Recipe match")
    print("-" * 60)
    user_input = "Can you review this Python function for me?"
    result = assembler.assemble(user_input)
    print(f"Input: {user_input}")
    print(f"Recipe matched: {result.recipe_name}")
    print(f"Infrastructure skills loaded: {len(result.infrastructure_skills)}")
    print(f"Task skills loaded: {len(result.task_skills)}")
    print(f"Total prompt length: {len(result.prompt)} chars")
    
    if result.errors:
        print(f"\nErrors encountered: {result.errors}")
    
    print("\n" + "=" * 60)
    print("Demo complete. See README.md for setup instructions.")


if __name__ == "__main__":
    main()
