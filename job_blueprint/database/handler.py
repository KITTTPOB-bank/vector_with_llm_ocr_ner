from elasticsearch import Elasticsearch
from typing import List
from base_model.model import ResumeExtraction
import json

es = Elasticsearch("http://localhost:9200")
if not es.ping():
    raise ConnectionError("Could not connect to Elasticsearch!")

def import_skil(experience_list: ResumeExtraction, index_name: str = "skills_by_position"):
    print(experience_list)
    print(type(experience_list))
    
    for  exp in experience_list.skills_by_position:
        print(exp)
        doc = {
            "skill": exp.skill,
            "year": exp.year,
            "position": exp.position
        }
        es.index(index=index_name,  document=doc)


    return f"Successfully"

def import_course():
    return [
        {
            "course": "สร้าง Real-Time Web App ด้วย Socket.io, Next.js 15.x และ Drizzle ORM (MySQL)",
            "keyword": [
                "TypeScript",
                "Socket.io",
                "Node.js",
                "Realtime",
                "Dashboard",
                "Chart",
                "Next.js",
                "Material UI",
                "shadcn/ui",
                "Drizzle ORM",
                "MySQL",
                "Build",
                "Deploy",
                "Production"
            ]
        }
    ]

