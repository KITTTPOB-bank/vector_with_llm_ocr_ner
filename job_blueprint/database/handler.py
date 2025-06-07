from elasticsearch import Elasticsearch
from typing import List
from base_model.model import ResumeExtraction
import json
def import_skil(experience_list: ResumeExtraction, index_name: str = "skills_by_position"):
    es = Elasticsearch("http://localhost:9200")

    if not es.ping():
        raise ConnectionError("Could not connect to Elasticsearch!")
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
