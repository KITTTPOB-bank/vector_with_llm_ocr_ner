from pydantic import BaseModel, Field
from typing import List

class SkillExperience(BaseModel):
    skill: List[str] = Field(description="List of technical or programming skills used in the specified position.")
    year: int = Field(description="The most recent calendar year the skill(s) were used in that position.")
    position: str = Field(description="The job title or role where the skill(s) were applied (e.g., Software Developer).")

class ResumeExtraction(BaseModel):
    skills_by_position: List[SkillExperience] = Field(description="A list of grouped skills by job position.")

class SkillExperience(BaseModel):
    skill: List[str]
    year: int
    position: str