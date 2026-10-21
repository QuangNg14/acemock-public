import uuid

from pydantic import BaseModel, ConfigDict

from app.models.base import Difficulty, QuantCategory, Round, Track


class QuestionOut(BaseModel):
    id: uuid.UUID
    company: str
    role_category: str | None
    track: Track
    round: Round
    difficulty: Difficulty | None
    title: str
    prompt: str
    topics: str | None
    leetcode_number: int | None
    # solution is intentionally omitted from the public shape (Pro-gated separately).
    model_config = ConfigDict(from_attributes=True)


class StartMockIn(BaseModel):
    company: str
    track: Track = Track.swe
    round: Round = Round.coding
    question_id: uuid.UUID | None = None


class TurnOut(BaseModel):
    position: int
    speaker: str
    content: str
    is_hint: bool
    model_config = ConfigDict(from_attributes=True)


class MockSessionOut(BaseModel):
    id: uuid.UUID
    company: str
    track: Track
    round: Round
    status: str
    hints_used: int
    question: QuestionOut | None = None
    turns: list[TurnOut] = []


class MessageIn(BaseModel):
    content: str


class ScorecardOut(BaseModel):
    overall: float
    recommendation: str
    breakdown: list[dict]
    strengths: str | None
    improvements: str | None


class StoryIn(BaseModel):
    title: str
    situation: str
    task: str
    action: str
    result: str
    target_companies: list[str] = []


class StoryOut(BaseModel):
    id: uuid.UUID
    title: str
    mapped_values: list[dict] = []
    target_companies: list[str] = []


class DrillIn(BaseModel):
    story_id: uuid.UUID
    company: str
    value_probed: str
    answer: str


class DrillOut(BaseModel):
    score: float | None
    structure_score: float | None
    specificity_score: float | None
    feedback: str | None
    followups: list[str] = []


class QuantDrillOut(BaseModel):
    id: uuid.UUID
    category: QuantCategory
    difficulty: Difficulty
    firm_tracks: str | None
    prompt: str
    time_limit_seconds: int | None
    model_config = ConfigDict(from_attributes=True)


class QuantAttemptIn(BaseModel):
    drill_id: uuid.UUID
    response: str
    elapsed_seconds: float | None = None


class QuantAttemptOut(BaseModel):
    correct: bool
    feedback: str | None
    reasoning_quality: float | None = None


class TTSIn(BaseModel):
    text: str


class CheckoutIn(BaseModel):
    plan: str = "pro"


class CheckoutOut(BaseModel):
    url: str


class BillingMeOut(BaseModel):
    authenticated: bool
    is_pro: bool
    email: str | None = None


class SolutionOut(BaseModel):
    solution: str | None = None
    answer: str | None = None
    solution_steps: str | None = None

