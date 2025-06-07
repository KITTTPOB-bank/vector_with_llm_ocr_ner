from base_model.model import ResumeExtraction , CourseExtraction
from elasticsearch import AsyncElasticsearch
import pandas as pd

es = AsyncElasticsearch("http://elasticsearch:9200")

 
async def connect():
    return es

async def import_skil(experience_list: ResumeExtraction,  desired_job: str, has_worked: bool, index_name: str = "resumes"):
    es = await connect()  
    count = 0
    for exp in experience_list.skills_by_position:
        doc = {
            "skill": exp.skill,  
            "year": exp.year,
            "position": exp.position.lower(),   
            "desired_job": experience_list.job_title.lower(),
            "has_worked": has_worked
        }
        await es.index(index=index_name, document=doc)
        count += 1
    return {"status": "success", "indexed_count": count, "message": "Skills imported successfully"}

async def import_course(course_skill : CourseExtraction , course_name: str, link: str ,index_name: str = "courses"):
    es = await connect()  
    doc = {
        "skill": course_skill.skill,
        "course_name": course_name,
        "link": link

    }
    await es.index(index=index_name, document=doc)
    return {"status": "success", "message": "Course imported successfully"}

async def moive_to_db(index_name: str = "movie"):
    es = await connect()  
    df = pd.read_csv("database/Data for Test movie_dataset - AI Engineer.csv")

    cols_to_embed = ["movie_title", "director_name", "genres", "plot_keywords", "title_year", "content_rating"]
    df[cols_to_embed] = df[cols_to_embed].fillna("")

    df = df[cols_to_embed + ["movie_imdb_link"]].dropna(subset=cols_to_embed) 

    for i, row in df.iterrows():
        text = " | ".join([str(row[col]) for col in cols_to_embed])
        doc = {
                "content": text,
                "movie_imdb_link": row["movie_imdb_link"]
            }
        await es.index(index=index_name, document=doc)
     
    return f"✅ Indexed {len(df)} movies to index: {index_name}"
 
    