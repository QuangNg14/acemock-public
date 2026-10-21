"""Prompt builder for grading free-text quant answers (brainteaser / probability).

Mental-math and market-making correctness is checked deterministically in the service
layer; this prompt handles reasoning-style answers where partial credit matters.
"""

import json


def quant_grader_prompt(category: str, prompt: str, reference_answer: str, response: str) -> str:
    schema = {
        "correct": "bool (final answer matches the reference within tolerance)",
        "reasoning_quality": "float 1-5",
        "feedback": "str, name the exact step that went wrong if any",
    }
    return (
        f"Category: {category}\n"
        f"Problem: {prompt}\n"
        f"Reference answer: {reference_answer}\n"
        f"Candidate response: {response}\n\n"
        f"Judge whether the final answer is correct and rate the reasoning. "
        f"Return JSON matching:\n{json.dumps(schema, indent=2)}"
    )
