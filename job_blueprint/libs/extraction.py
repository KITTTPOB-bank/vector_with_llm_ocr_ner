from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from base_model.model import ResumeExtraction
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
    print(skill)
    return skill

def llm_extraction(skill : list , resume : str, model: str) -> ResumeExtraction:
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    prompt = f"""
You are a professional resume parser.

Your task is to extract and group technical skills used in real work experiences such as **job positions** (e.g., Software Developer, Business Analyst) from the resume below.

---

### Skill List (Extracted from Resume):
Use only these skills when generating your output:
{skill}

---

### Output Format:
Return a list of entries. Each entry must include:
- `skill`: A list of relevant technical skills used in that specific job.
- `year`: The **most recent calendar year** the experience was active.
  - For example:
    - "2023 - 2024" → use 2024
    - "2020 – Present" → use 2025
- `position`: The full name or title of the **job or role** where the skills were applied.

---

### Guidelines:

- Only include **actual job experiences** or **technical work**.
  ❌ Exclude education, awards, coursework, and certifications.

- If a **skill is mentioned but the year it was used is not clear**, **do not include it** in the output.

- If **dates appear below, above, or far from the position title**, infer that those dates likely belong to the nearest or most relevant job title nearby.

- If a job is **missing a date entirely**, but nearby dates exist (before or after), you may **reasonably estimate** the correct year from the context and structure of the resume.

- Group multiple skills used in the same job under a single record.

- Only include skills that are found in the provided skill list — do not include unrelated tools or general concepts.

- Do not invent or assume jobs or skills beyond what is stated in the resume.

---

### Example Output:
[
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
]

---

### Resume:
<resume>
{resume}
</resume>
"""
    llm = ChatOpenAI(api_key=OPENAI_KEY, temperature=0 , model=model).with_structured_output(ResumeExtraction)
    responed : ResumeExtraction = llm.invoke(prompt)
    return responed 
   