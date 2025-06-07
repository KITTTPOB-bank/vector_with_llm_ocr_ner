from base_model.model import ResumeExtraction , CourseExtraction
from elasticsearch import AsyncElasticsearch

es = AsyncElasticsearch("http://localhost:9200")

 
async def connect():
    return es

async def import_skil(experience_list: ResumeExtraction,  desired_job: str, has_worked: bool, index_name: str = "resumes"):
    es = await connect()  
    count = 0
    for exp in experience_list.skills_by_position:
        doc = {
            "skill": exp.skill,
            "year": exp.year,
            "position": exp.position,
            "desired_job" : experience_list.job_title,
            "has_worked" : has_worked
        }
        await es.index(index=index_name, document=doc)
        count += 1
    return {"status": "success", "indexed_count": count, "message": "Skills imported successfully"}

async def import_course(course_skill : CourseExtraction , course_name: str, index_name: str = "courses"):
    es = await connect()  
    doc = {
        "skill": course_skill.skill,
        "course_name": course_name
    }
    await es.index(index=index_name, document=doc)
    return {"status": "success", "message": "Course imported successfully"}


