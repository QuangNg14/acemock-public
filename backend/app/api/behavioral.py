import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.prompts.behavioral_coach import behavioral_grader_prompt, value_mapping_prompt
from app.db import get_db
from app.models.behavioral import BehavioralDrill, BehavioralStory
from app.models.user import User
from app.schemas.dto import DrillIn, DrillOut, StoryIn, StoryOut
from app.services import llm
from app.services.auth import current_user_optional

router = APIRouter(prefix="/behavioral", tags=["behavioral"])


def _story_text(s: StoryIn) -> str:
    return f"S: {s.situation}\nT: {s.task}\nA: {s.action}\nR: {s.result}"


@router.post("/stories", response_model=StoryOut)
async def create_story(
    body: StoryIn,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> StoryOut:
    company = body.target_companies[0] if body.target_companies else "a top tech company"
    mapping = llm.complete_json(
        system="You map STAR stories to company values. Return only JSON.",
        user=value_mapping_prompt(company, _story_text(body)),
    )
    mapped = mapping.get("items", mapping if isinstance(mapping, list) else [])

    story = BehavioralStory(
        user_id=user.id if user else None,
        title=body.title,
        situation=body.situation,
        task=body.task,
        action=body.action,
        result=body.result,
        mapped_values=json.dumps(mapped),
        target_companies=json.dumps(body.target_companies),
    )
    db.add(story)
    await db.commit()
    await db.refresh(story)
    return StoryOut(
        id=story.id,
        title=story.title,
        mapped_values=mapped if isinstance(mapped, list) else [],
        target_companies=body.target_companies,
    )


@router.post("/drills", response_model=DrillOut)
async def grade_drill(body: DrillIn, db: AsyncSession = Depends(get_db)) -> DrillOut:
    story = await db.get(BehavioralStory, body.story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="story not found")

    question = f"Tell me about a time you demonstrated {body.value_probed}."
    result = llm.complete_json(
        system="You are a strict behavioral interviewer. Return only JSON.",
        user=behavioral_grader_prompt(body.company, body.value_probed, question, body.answer),
    )
    followups = result.get("followups", [])
    drill = BehavioralDrill(
        story_id=story.id,
        company=body.company,
        value_probed=body.value_probed,
        question=question,
        answer=body.answer,
        score=result.get("score"),
        structure_score=result.get("structure_score"),
        specificity_score=result.get("specificity_score"),
        feedback=result.get("feedback"),
        followups=json.dumps(followups),
    )
    db.add(drill)
    await db.commit()
    return DrillOut(
        score=drill.score,
        structure_score=drill.structure_score,
        specificity_score=drill.specificity_score,
        feedback=drill.feedback,
        followups=followups,
    )


@router.get("/stories/{story_id}", response_model=StoryOut)
async def get_story(story_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> StoryOut:
    story = await db.get(BehavioralStory, story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="story not found")
    return StoryOut(
        id=story.id,
        title=story.title,
        mapped_values=json.loads(story.mapped_values) if story.mapped_values else [],
        target_companies=json.loads(story.target_companies) if story.target_companies else [],
    )
