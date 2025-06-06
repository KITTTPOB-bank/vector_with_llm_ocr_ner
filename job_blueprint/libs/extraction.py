from dotenv import load_dotenv
from spacy_llm.util import assemble
from spacy.tokens import Doc
from spacy.util import load_config
from convect import pdf_to_markdown_MistralOCR, pdf_to_markdown, pdf_to_markdown_EasyOCR, any_to_markdown

load_dotenv()
config = load_config("config.cfg")
nlp = assemble("config.cfg")
 
res = pdf_to_markdown("C:/Users/USER/Downloads/resume.pdf")

text = res
print("----------")
print(text)
doc = nlp(text)
print(doc.ents)

# def pair_skills_with_durations(doc: Doc):
#     skills = []
#     durations = []
#     job = []
#     for ent in doc.ents:
#         if ent.label_ == "RESUME_SKILL":
#             skills.append((ent.text, ent.start))
#         elif ent.label_ == "SKILL_DURATION":
#             durations.append((ent.text, ent.start))
#         elif ent.label_ == "JOB_EXP":
#             job.append(ent.text)
#     result = []
#     print("---------------------------------------------------------")
#     print(skills)
#     print(durations)
#     print("---------------------------------------------------------")

#     for skill, skill_idx in skills:
#         nearest = min(durations, key=lambda d: abs(d[1] - skill_idx), default=None)
#         result.append({
#             "skill": skill,
#             "duration": nearest[0] if nearest else None
#         })

#     token_count = len([token for token in doc if not token.is_space])

#     return {
#         "tokens_used": token_count,
#         "skills_with_durations": result,
#         "job_exp": job,
#     }

# result = pair_skills_with_durations(doc)
# print("======================================================================================")
# print(result)
# print("======================================================================================")

