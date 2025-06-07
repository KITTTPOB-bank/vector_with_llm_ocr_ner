import json
from types import CoroutineType
from typing import Type, Union
from langchain_core.tools import StructuredTool
from pydantic import BaseModel
from database.elastic import connect
from libs.retrieval import hybrid_search
import json
from datetime import datetime
def structool(name : str, desc : str, func :  CoroutineType,   args: Union[Type[BaseModel], None] = None) -> StructuredTool:
    tool = StructuredTool.from_function(
        coroutine=func,
        name=name,
        description=desc,
        args_schema=args
    )
    return tool

 
def create_movie_tool() -> list[StructuredTool]:
    tools = []

    async def get_movie(query: str) -> str:
        responed = await hybrid_search(query)
        return str(responed)

    tools.append(structool(
        "get_movie",
        "ส่งคำค้นหา เป็นรูปแบบ ภาษาอังกฤษ เน้นเป็น keyword.",
        get_movie
    ))
    return tools

def create_tool() -> list[StructuredTool]:
    tools = []

    async def recommend_skill_for_position(position: str) -> str:
        es = await connect()
        query = {
        "size": 0,   
          "query": {
            "match": {
                "position": {
                    "query": position,
                    "fuzziness": "AUTO"
                }
            }
        },
        "aggs": {
            "popular_skills": {
                "terms": {
                    "field": "skill.keyword",
                    "size": 10 
                }
            }
        }
    }
        res = await es.search(index="resumes", body=query)
        aggregations = res.get("aggregations", {})

        if not aggregations:
            return f"ไม่พบตำแหน่งงาน '{position}' หรือไม่มีสกิลในฐานข้อมูล"

        buckets = aggregations["popular_skills"]["buckets"]

        popular_skills = [{"skill": b["key"], "count": b["doc_count"]} for b in buckets]

        result = {
            "position": position,
            "popular_skills": popular_skills
        }

        return json.dumps(result, ensure_ascii=False)
    
    async def search_courses_by_skills(skills: list[str]) -> str:
        es = await connect()
        query = {
            "query": {
                "bool": {
                    "should": [{"term": {"skill.keyword": skill}} for skill in skills]
                }
            },
            "size": 5,
            "_source": ["course_name", "skill"],
            "sort": [
                {"_score": {"order": "desc"}}   
            ]
        }
        try:
            response = await es.search(index="courses", body=query)
            hits = response.get("hits", {}).get("hits", [])
            results = [
                {
                    "course_name": hit["_source"]["course_name"],
                    "matched_skills": [skill for skill in skills if skill in hit["_source"].get("skill", [])],
                    "all_skills": hit["_source"].get("skill", []),
                    "link": hit["_source"].get("link", [])
                }
                for hit in hits
            ]
            return json.dumps(results, ensure_ascii=False)
        except Exception as e:
            return str(e)
        
    async def popular_field_by_year(year: int, field: str, size: int = 3) -> str:
        es = await connect()

        agg_field = f"{field}.keyword"

        query_agg = {
            "size": 0,
            "query": {
                "term": {
                    "year": year
                }
            },
            "aggs": {
                "popular_items": {
                    "terms": {
                        "field": agg_field,
                        "size": size,
                        "order": {"_count": "desc"}
                    }
                }
            }
        }

        res = await es.search(index="resumes", body=query_agg)
        agg = res.get("aggregations", {})
        popular_items = [bucket["key"] for bucket in agg.get("popular_items", {}).get("buckets", [])]

        return json.dumps({
            "year": year,
            "field": field,
            "top": size,
            "most_popular_items": popular_items
        }, ensure_ascii=False)
    
    async def job_blueprint(year: int, keyword: str) -> str:
        es = await connect()

        query_agg = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {"term": {"year": year}},
                        {
                            "multi_match": {
                                "query": keyword,
                                "fields": ["position", "desired_job", "skill"]
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "popular_skills": {
                    "terms": {
                        "field": "skill.keyword",
                        "size": 10
                    }
                },
                "positions": {
                    "terms": {
                        "field": "position.keyword",
                        "size": 10
                    },
                    "aggs": {
                        "top_skills": {
                            "terms": {
                                "field": "skill.keyword",
                                "size": 5
                            }
                        }
                    }
                }
            }
        }

        res = await es.search(index="resumes", body=query_agg)
        agg = res.get("aggregations", {})

        positions_skills = {}
        for pos_bucket in agg.get("positions", {}).get("buckets", []):
            pos = pos_bucket["key"]
            top_skills = [skill["key"] for skill in pos_bucket["top_skills"]["buckets"]]
            positions_skills[pos] = top_skills

        popular_skills = [bucket["key"] for bucket in agg.get("popular_skills", {}).get("buckets", [])]

        return json.dumps({
            "year": year,
            "keyword": keyword,
            "most_popular_skills_overall": popular_skills,
            "positions_top_skills": positions_skills
        }, ensure_ascii=False)
    
    tools.append(structool(
        name="popular_skills_by_year",
        description=f"For a given year and keyword, summarize the most demanded skills overall and by job position. Current time: {datetime.now()}",
        func=job_blueprint
    ))
    
    tools.append(structool(
        "popular_field_by_year",
        f"Get top N popular values for a given field in the resume index for a specific year. "
        f"Parameters: year (int), field (e.g., 'skill', 'position', 'desired_job'), size (optional, int, default=3). "
        f"Date now: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        popular_field_by_year
    ))

    tools.append(structool(
        "search_courses_by_skills",
        "Search courses that teach any of the given skills. ",
        
        search_courses_by_skills
    ))

    tools.append(structool(
        "recommend_skill_for_position",
        "ใช้สำหรับค้นหาว่า ตำแหน่งนี้ ทักษะไหนนิยม เพื่อนำไปค้นหา คอสต่อไป.",
        recommend_skill_for_position
    ))


    return tools
