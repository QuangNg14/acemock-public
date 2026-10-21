"""Prompt builders for the Behavioral Engine.

Two jobs: (1) map a raw STAR story to the company's values / leadership principles,
(2) grade a behavioral answer for structure and specificity and generate follow-ups.
"""

import json


def value_mapping_prompt(company: str, story: str) -> str:
    return (
        f"Company: {company}\n"
        f"Candidate STAR story:\n{story}\n\n"
        f"List which of {company}'s published values or leadership principles this story "
        f"evidences, strongest first. For each, name the principle and the one sentence from "
        f"the story that demonstrates it. Return a JSON array of "
        f'{{"value": str, "evidence": str}}.'
    )


def behavioral_grader_prompt(company: str, value_probed: str, question: str, answer: str) -> str:
    schema = {
        "score": "float 1-5 overall",
        "structure_score": "float 1-5 (clear S-T-A-R, no rambling)",
        "specificity_score": "float 1-5 (concrete metrics, ownership, first-person action)",
        "feedback": "str, 2-3 sentences, actionable",
        "followups": ["str probing follow-up the interviewer would actually ask"],
    }
    return (
        f"You are a {company} behavioral interviewer probing for: {value_probed}.\n"
        f"Question asked: {question}\n"
        f"Candidate answer:\n{answer}\n\n"
        f"Grade strictly. Penalize vague 'we' language, missing result metrics, and "
        f"stories that do not actually evidence {value_probed}. "
        f"Return JSON matching:\n{json.dumps(schema, indent=2)}"
    )
