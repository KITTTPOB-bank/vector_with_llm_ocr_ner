from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from base_model.model import ResumeExtraction , CourseExtraction
from spacy_llm.util import assemble
load_dotenv()



async def spacy_extraction(markdown: str) -> list:
    skill = []
    base_dir = os.path.dirname(__file__)
    config_path = os.path.join(base_dir, "config.cfg")
    ner = assemble(config_path)
    doc = ner(markdown)
    for ent in doc.ents:
        skill.append(ent.text)
    return skill

async def course_extraction(context : str, model: str):
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    prompt = f"""
You are a professional skill extraction system.

Your task is to extract **all relevant skills** mentioned in the course description below.

Please ensure:
- If the same skill appears multiple times, include it only once in the output.

Return the result in the following JSON format:
### Example Output:
[
  {{
    "skill": ["React", "TypeScript", "AWS"],
  }}
]

---

### course description:
<course description>
{context}
</course description>
"""
    llm = ChatOpenAI(api_key=OPENAI_KEY, temperature=0 , model=model).with_structured_output(CourseExtraction)
    responed : CourseExtraction = await llm.ainvoke(prompt)
    return responed 
   

async def llm_extraction(skill : list , resume : str, model: str) -> ResumeExtraction:
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    prompt = f"""
You are a professional resume parser.

Your task is to extract and group technical skills used in real work experiences such as **job positions** (e.g., Software Developer, Business Analyst) from the resume below.

In addition, extract the **job title**, which means the main or primary job title emphasized or highlighted in the resume content.  
This is the key job title presented as the applicant’s main role or focus in the resume.  
If no such main job title is found, return an empty string "" for that field.

---

### Skill List (Extracted from Resume):
Use only these skills when generating your output.  
If the list is empty or not provided ([]), extract relevant technical skills directly from the resume content instead:

{skill}

---

### Output Format:
Return a list of entries. Each entry must include:
- skill: A list of relevant technical skills used in that job.
- year: The **most recent calendar year** the experience was active.
  - For example:
    - "2023 - 2024" → use 2024
    - "2020 – Present" → use 2025
- position: The full name or title of the **job or role** where the skills were applied.
- job_title: The main or primary job title emphasized in the resume, extracted as described above.  
  If none found, return an empty string "".

---

### Guidelines:

- If a **skill is mentioned but the year it was used is not clear**, **do not include it** in the output.

- If **dates appear below, above, or far from the position title**, infer that those dates likely belong to the nearest or most relevant job title nearby.

- If a job is **missing a date entirely**, but nearby dates exist (before or after), you may **reasonably estimate** the correct year from the context and structure of the resume.

- Group multiple skills used in the same job under a single record.

- Only include skills that are found in the provided skill list — do not include unrelated tools or general concepts.

- Do not invent or assume jobs or skills beyond what is stated in the resume.

---

### Example Output:
{{
  "skills_by_position": [
    {{
      "skill": ["React", "TypeScript", "AWS"],
      "year": 2024,
      "position": "Software Engineer"
    }},
    {{
      "skill": ["Java", "JUnit"],
      "year": 2023,
      "position": "Backend Developer"
    }}
  ],
  "job_title": "Senior Software Engineer"
}}

---

### Resume:
<resume>
{resume}
</resume>
"""

    llm = ChatOpenAI(api_key=OPENAI_KEY, temperature=0 , model=model).with_structured_output(ResumeExtraction)
    responed : ResumeExtraction = await llm.ainvoke(prompt)
    return responed 
   