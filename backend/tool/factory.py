import json
from types import CoroutineType
from typing import Type, Union
from elastic_transport import ObjectApiResponse
from langchain_core.tools import StructuredTool
from pydantic import BaseModel
from database.elastic import connect
import json
 
def structool(name : str, desc : str, func :  CoroutineType,   args: Union[Type[BaseModel], None] = None) -> StructuredTool:
    tool = StructuredTool.from_function(
        coroutine=func,
        name=name,
        description=desc,
        args_schema=args
    )
    return tool

 

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
        print(res)
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

    async def search_es(index: str, query: dict = {}) -> str:
        es = await connect()
        try:
            response = await es.search(index=index, body=query)
            return json.dumps(response, ensure_ascii=False)
        except Exception as e:
            return str(e)
    async def popular_skills_by_year(year: int) -> str:
        es = await connect()

        query_agg = {
            "size": 0,
            "query": {
                "term": {
                    "year": year
                }
            },
            "aggs": {
                "popular_skills": {
                    "terms": {
                        "field": "skill.keyword",
                        "size": 10,
                        "order": {"_count": "desc"}
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
                                "size": 5,
                                "order": {"_count": "desc"}
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
            "most_popular_skills_overall": popular_skills,
            "positions_top_skills": positions_skills
        }, ensure_ascii=False)
    
 

    tools.append(structool(
        "search_courses_by_skills",
        "Search courses that teach any of the given skills.",
        search_courses_by_skills
    ))

    # tools.append(structool(
    #     "search_es",
    #     (
    #         "Execute an Elasticsearch query on a given index and return raw results as JSON.\n"
    #         "The query parameter must be a valid Elasticsearch DSL JSON.\n\n"
    #         "Database schemas:\n"
    #         "1) Index 'courses':\n"
    #         "   - skill: list of skill strings (e.g. ['TypeScript', 'Next.js'])\n"
    #         "   - course_name: string\n\n"
    #         "2) Index 'resumes':\n"
    #         "   - skill: list of skill strings\n"
    #         "   - year: integer (e.g. 2023)\n"
    #         "   - position: string (job title)\n"
    #         "   - desired_job: string\n"
    #         "   - has_worked: boolean\n\n"
    #         "Example query to search courses by skills:\n"
    #         '{ "query": { "bool": { "should": [ {"term": {"skill.keyword": "Next.js"}}, {"term": {"skill.keyword": "TypeScript"}} ] } } }'
    #     ),
    #     search_es
    # ))

    tools.append(structool(
        "recommend_skill_for_position",
        "ใช้สำหรับค้นหาว่า ตำแหน่งนี้ ทักษะไหนนิยม เพื่อนำไปค้นหา คอสต่อไป.",
        recommend_skill_for_position
    ))

    # tools.append(structool(
    #     "popular_skills_by_year",
    #     "For a given year, summarize the most demanded skills overall and by job position.",
    #     popular_skills_by_year
    # ))

    return tools
