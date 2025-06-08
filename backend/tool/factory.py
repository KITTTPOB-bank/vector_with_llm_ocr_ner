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
        print("use hybrid_search .... ")
        print(query)

        responed = await hybrid_search(query)

        print(responed)
        return str(responed)

    tools.append(structool(
    "get_movie",
    "Provide a general search query in English, using keyword-style formatting (e.g., omit stopwords and punctuation).",
    get_movie
))
    return tools

def create_tool() -> list[StructuredTool]:
    tools = []

    async def recommend_skill_for_position(position: str) -> str:
        print("use recommend_skill_for_position .... ")

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
        print("use search_courses_by_skills .... ")

        es = await connect()
        query = {
            "query": {
                "bool": {
                    "should": [{"term": {"skill.keyword": skill}} for skill in skills]
                }
            },
            "size": 5,
            "_source": ["course_name", "skill" , "link"],
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

        print("use popular_field_by_year .... ")
        
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
    
    async def job_blueprint( position: str) -> str:
        es = await connect()

        print("use job_blueprint .... ")

        query_agg = {
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
                "by_year": {
                    "terms": {
                    "field": "year",
                    "size": 10,
                    "order": {"_key": "desc"}
                    },
                    "aggs": {
                        "positions": {
                            "terms": {"field": "position.keyword", "size": 10},
                            "aggs": {
                            "top_skills": {
                                "terms": {"field": "skill.keyword", "size": 5}
                            }
                            }
                        },
                        "desired_jobs": {
                            "terms": {"field": "desired_job.keyword", "size": 5},
                            "aggs": {
                            "desired_top_skills": {
                                "terms": {"field": "skill.keyword", "size": 3}
                            }
                            }
                        }
                    }
                }
            }
        }
        results_by_year = {}
        res = await es.search(index="resumes", body=query_agg)
        agg = res.get("aggregations", {})
        for year_bucket in agg.get("by_year", {}).get("buckets", []):
            year = year_bucket["key"]
    
            positions_skills = {}
            for pos_bucket in year_bucket.get("positions", {}).get("buckets", []):
                pos = pos_bucket["key"]
                top_skills = [skill["key"] for skill in pos_bucket.get("top_skills", {}).get("buckets", [])]
                positions_skills[pos] = top_skills

            desired_jobs_skills = {}
            for dj_bucket in year_bucket.get("desired_jobs", {}).get("buckets", []):
                job = dj_bucket["key"]
                top_skills = [skill["key"] for skill in dj_bucket.get("desired_top_skills", {}).get("buckets", [])]
                desired_jobs_skills[job] = top_skills

            results_by_year[year] = {
                "positions_top_skills": positions_skills,
                "desired_jobs_top_skills": desired_jobs_skills 
            }
        
        print(results_by_year)

        return json.dumps(results_by_year, ensure_ascii=False, indent=2)

    tools.append(structool(
        "job_blueprint",
        "For a given job position, summarize the most demanded skills overall and by job position, returning structured data grouped by year, including popular skills, position-specific skills, and desired job-specific skills.",
        job_blueprint
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
        "Search courses that teach any of the given skills and return the full list of matched skills along with course details and links to the user.",
        search_courses_by_skills
    ))

    tools.append(structool(
    "recommend_skill_for_position",
    (
        "Recommend popular technical skills commonly used in the specified job position "
        "Useful for planning learning paths or choosing the right training courses"
    ),
    recommend_skill_for_position
    ))
    return tools
