from elasticsearch import Elasticsearch
from typing import List
from base_model.model import SkillExperience


def import_skil(experience_list: List[SkillExperience], index_name: str = "skill-experiences"):
    es = Elasticsearch("http://localhost:9200")

    if not es.ping():
        raise ConnectionError("Could not connect to Elasticsearch!")

    for i, exp in enumerate(experience_list):
        doc = {
            "skill": exp.skill,
            "year": exp.year,
            "position": exp.position
        }
        es.index(index=index_name, id=i, document=doc)

    print(f"Successfully indexed {len(experience_list)} documents to '{index_name}'.")
