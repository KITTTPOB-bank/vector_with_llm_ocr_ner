import json
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class structool:
    name: str
    description: str
    func: callable

async def connect():
    # ตัวอย่างเชื่อมต่อ Elasticsearch
    from elasticsearch import AsyncElasticsearch
    es = AsyncElasticsearch(hosts=["http://localhost:9200"])
    return es

def create_tool() -> List[structool]:
    tools = []

    async def search_es(index: str, query: dict = {}) -> str:
        es = await connect()
        try:
            response = await es.search(index=index, body=query)
            return json.dumps(response, ensure_ascii=False)
        except Exception as e:
            return str(e)

    async def recommend_courses_for_position(position: str) -> str:
        es = await connect()
        # 1. หาตำแหน่งงานใน index resumes พร้อมดึง skill list ออกมา
        query_resume = {
            "query": {
                "match": {
                    "position": position
                }
            }
        }
        res = await es.search(index="resumes", body=query_resume)
        skills = set()
        for hit in res["hits"]["hits"]:
            skills.update(hit["_source"].get("skill", []))
        if not skills:
            return f"ไม่พบตำแหน่งงาน '{position}' ในฐานข้อมูล"

        # 2. หาคอร์สที่มีสกิลเหล่านี้ใน index courses
        query_courses = {
            "query": {
                "bool": {
                    "should": [
                        {"terms": {"skill.keyword": list(skills)}}
                    ]
                }
            }
        }
        res_courses = await es.search(index="courses", body=query_courses)
        courses = []
        for hit in res_courses["hits"]["hits"]:
            courses.append(hit["_source"]["course_name"])

        return json.dumps({
            "position": position,
            "required_skills": list(skills),
            "recommended_courses": courses
        }, ensure_ascii=False)

    async def popular_skills_by_year(year: int) -> str:
        es = await connect()
        # Aggregate skills by frequency for given year in resumes index
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

        # สรุปผลเป็นตำแหน่งกับสกิลที่ต้องการสูงสุด
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
    async def search_courses_by_skills(skills: List[str]) -> str:
        es = await connect()
        query = {
            "query": {
                "bool": {
                    "should": [{"term": {"skill.keyword": skill}} for skill in skills]
                }
            }
        }
        try:
            response = await es.search(index="courses", body=query)
            return json.dumps(response, ensure_ascii=False)
        except Exception as e:
            return str(e)

    tools.append(structool(
        name="search_courses_by_skills",
        description="Search courses that teach any of the given skills.",
        func=search_courses_by_skills
    ))

    tools.append(structool(
        name="search_es",
        description=(
            "Execute an Elasticsearch query on a given index and return raw results as JSON.\n"
            "The query parameter must be a valid Elasticsearch DSL JSON.\n\n"
            "Database schemas:\n"
            "1) Index 'courses':\n"
            "   - skill: list of skill strings (e.g. ['TypeScript', 'Next.js'])\n"
            "   - course_name: string\n\n"
            "2) Index 'resumes':\n"
            "   - skill: list of skill strings\n"
            "   - year: integer (e.g. 2023)\n"
            "   - position: string (job title)\n"
            "   - desired_job: string\n"
            "   - has_worked: boolean\n\n"
            "Example query to search courses by skills:\n"
            '{ "query": { "bool": { "should": [ {"term": {"skill.keyword": "Next.js"}}, {"term": {"skill.keyword": "TypeScript"}} ] } } }'
        ),
        func=search_es
    ))
    tools.append(structool(
        name="recommend_courses_for_position",
        description="Given a job position, recommend relevant courses based on required skills extracted from resumes.",
        func=recommend_courses_for_position
    ))

    tools.append(structool(
        name="popular_skills_by_year",
        description="For a given year, summarize the most demanded skills overall and by job position.",
        func=popular_skills_by_year
    ))

    return tools
