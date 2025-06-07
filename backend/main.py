from fastapi import FastAPI, File, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from agent import chat
import os
from libs.extraction import spacy_extraction, llm_extraction, course_extraction
from libs.convect import pdf_to_markdown , pdf_to_markdown_EasyOCR , pdf_to_markdown_MistralOCR , any_to_markdown
from database.handler import import_skil, import_course
from base_model import model
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage , SystemMessage
from langchain_openai import ChatOpenAI
from tool import factory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_CONTEXT_MESSAGES = 15  
SUMMARY_TRIGGER_THRESHOLD = 30 
tools = factory.create_tool()


async def summarize_messages(messages: list[AnyMessage]) -> str:
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    text_blocks = []
    llm = ChatOpenAI(model="gpt-4.1-mini", stream_usage= True, temperature=0 , top_p=0, api_key=OPENAI_KEY)

    for msg in messages:
        prefix = "User: " if msg.role == "user" else "AI: "
        text_blocks.append(prefix + msg.content)
    
    full_text = "\n".join(text_blocks)

    summary_prompt = f"""
    สรุปข้อความต่อไปนี้ให้สั้นและกระชับเพื่อใช้เป็นบริบท:
    {full_text}
    """
    summary_response : AIMessage = await llm.ainvoke(messages=[HumanMessage(content=summary_prompt)])
    return summary_response.content

async def stream(messages: list):
    async for message in chat.call_agent(tools).astream_events({"messages" : messages}, version="v2"):
        if message["event"] == "on_chat_model_stream":
            if message["metadata"]["langgraph_node"] == "node_model":
                if message["data"]['chunk'].content:
                    yield message["data"]['chunk'].content

@app.post("/chat")
async def chat_stream(conversation : model.ChatMessages):
    messages = []
    all_messages = conversation.messages

    messages.append(SystemMessage(content="""
คุณคือผู้ช่วยอัจฉริยะด้านการแนะนำคอร์สเรียน, ทักษะ, เทรนด์งาน และโอกาสในการพัฒนาตนเอง
โปรดใช้ `get_elasticsearch_structure` ก่อนเมื่อไม่แน่ใจว่า index มี field อะไรให้ค้นหา

1. `get_elasticsearch_structure` — ใช้เพื่อดูโครงสร้าง (schema/field) ของข้อมูลทั้งหมดใน Elasticsearch

2. `elastic_search` — ใช้ค้นหาข้อมูล

 
เป้าหมายของคุณคือ:
- ช่วยแนะนำคอร์สเรียนที่เหมาะกับเป้าหมายของผู้ใช้
- วิเคราะห์แนวโน้มทักษะที่ตลาดงานต้องการ
- ให้คำแนะนำตามข้อมูลที่ดึงมาจาก Elasticsearch อย่างถูกต้องและชัดเจน
"""))

    if len(all_messages) > SUMMARY_TRIGGER_THRESHOLD:
        old_messages = all_messages[:-MAX_CONTEXT_MESSAGES]
        recent_messages = all_messages[-MAX_CONTEXT_MESSAGES:]
        summary = await summarize_messages(old_messages)
         
        messages.append(SystemMessage(content=f"สรุปบทสนทนาก่อนหน้านี้: {summary}"))
        for chat in recent_messages:
            if chat.role == "ai":
                messages.append(AIMessage(content=chat.content))
            else:
                messages.append(HumanMessage(content=chat.content))
    else:
        for chat in all_messages:
            if chat.role == "ai":
                messages.append(AIMessage(content=chat.content))
            else:
                messages.append(HumanMessage(content=chat.content))
    return StreamingResponse(stream(messages), media_type="text/event-stream")

@app.post("/course")
async def add_course(course : model.Course):
    ner =  await course_extraction(course.course_detail , "gpt-4.1-mini")
    status = await import_course(ner , course.name)
    return status


@app.post("/extract")
async def extract_text(
    file: UploadFile = File(...),
    read_by: str = Form("default"),
    desired_job: str = Form("", description="งานที่อยากได้"),       
    has_worked: bool = Form(False, description="ได้เข้าทำงานแล้วหรือยัง")     
):
    SAVE_DIR = "./files"
    os.makedirs(SAVE_DIR, exist_ok=True)  
    
    filename  = file.filename
    save_path = os.path.join(SAVE_DIR, filename)

    # if os.path.exists(save_path):
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"ไฟล์ '{filename}' มีอยู่แล้วในระบบ"
    #     )


    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)


    if read_by == "default" and filename.endswith(".pdf"):
        read_by = "pdf"
    
    try:
        match read_by:
            case "default":
                markdown = await any_to_markdown(save_path)
            case "pdf":
                markdown = await pdf_to_markdown(save_path)
            case "mistral":
                markdown = await pdf_to_markdown_MistralOCR(save_path)
            case "easy":
                markdown = await pdf_to_markdown_EasyOCR(save_path)
            case _:
                raise HTTPException(status_code=400, detail="Invalid OCR type. Choose: default, easy, mistral")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    if len(markdown) < 100:
        raise HTTPException(
            status_code=400,
            detail="ไม่สามารถสกัดเอกสารได้ ลองใช้เป็น `mistral`"
        )

    try:
        ner = await spacy_extraction(markdown)
        blueprint = await llm_extraction(ner, markdown, "gpt-4.1-mini" )
        status = await import_skil(blueprint , desired_job, has_worked)

        return status

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    
# from elasticsearch import Elasticsearch

# es = Elasticsearch("http://localhost:9200")

# query = {
#     "size": 0,
#     "query": {
#         "match_phrase": {
#             "position": "Fullstack Developer"
#         }
#     },
#     "aggs": {
#         "popular_skills": {
#             "terms": {
#                 "field": "skill.keyword",
#                 "size": 10
#             }
#         }
#     }
# }

# response = es.search(index="skills_by_position", body=query)

# # แสดงผลสกิลที่นิยมที่สุด
# for bucket in response['aggregations']['popular_skills']['buckets']:
#     print(f"Skill: {bucket['key']}, Count: {bucket['doc_count']}")



from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

# ดึงชื่อ index ทั้งหมด
indices = es.indices.get_alias(index="*").keys()

# ลบ index ทุกตัว
for index in indices:
    es.indices.delete(index=index)
    print(f"Deleted index: {index}")
