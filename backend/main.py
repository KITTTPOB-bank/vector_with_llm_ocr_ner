import asyncio
from fastapi import FastAPI, File, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from agent import chat
import os
from libs.extraction import spacy_extraction, llm_extraction, course_extraction
from libs.convect import pdf_to_markdown , pdf_to_markdown_EasyOCR , pdf_to_markdown_MistralOCR , any_to_markdown
from libs.retrieval import hybrid_search
from database.elastic import import_skil, import_course, moive_to_db, connect
from base_model import model
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage , SystemMessage
from langchain_openai import ChatOpenAI
from tool import factory
from dotenv import load_dotenv
from database.chroma import embedding_to_chroma
import asyncio

load_dotenv()

from contextlib import asynccontextmanager

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

async def summarize_messages(all_msg: list[AnyMessage]) -> str:
    messages = []
    if len(all_msg) > SUMMARY_TRIGGER_THRESHOLD:
        old_messages = all_msg[:-MAX_CONTEXT_MESSAGES]
        recent_messages = all_msg[-MAX_CONTEXT_MESSAGES:]

        OPENAI_KEY = os.getenv("OPENAI_API_KEY")

        text_blocks = []
        llm = ChatOpenAI(model="gpt-4.1-mini", stream_usage= True, temperature=0 , top_p=0, api_key=OPENAI_KEY)

        for msg in old_messages:
                prefix = "User: " if msg.role == "user" else "AI: "
                text_blocks.append(prefix + msg.content)
        
        full_text = "\n".join(text_blocks)

        summary_prompt = f"""
        สรุปข้อความต่อไปนี้ให้สั้นและกระชับเพื่อใช้เป็นบริบท:
        {full_text}
        """
        summary_response : AIMessage = await llm.ainvoke(messages=[HumanMessage(content=summary_prompt)])
        messages.append(SystemMessage(content=f"สรุปบทสนทนาก่อนหน้านี้: {summary_response}"))
        for chat in recent_messages:
            if chat.role == "ai":
                messages.append(AIMessage(content=chat.content))
            else:
                messages.append(HumanMessage(content=chat.content))
    else:
        for chat in all_msg:
            if chat.role == "ai":
                messages.append(AIMessage(content=chat.content))
            else:
                messages.append(HumanMessage(content=chat.content))

    return messages

async def stream(messages: list , tools_choice: list):
    async for message in chat.call_agent(tools_choice).astream_events({"messages" : messages}, version="v2"):
        if message["event"] == "on_chat_model_stream":
            if message["metadata"]["langgraph_node"] == "node_model":
                if message["data"]['chunk'].content:
                    yield message["data"]['chunk'].content

@app.post("/chatJob")
async def chat_stream(conversation : model.ChatMessages):
    tools_choice = tools
    messages = await summarize_messages(conversation.messages)
    return StreamingResponse(stream(messages , tools_choice), media_type="text/event-stream")

@app.post("/chatMovie")
async def chat_stream(conversation : model.ChatMessages):
    messages = []
    messages = await summarize_messages(conversation.messages)
    return StreamingResponse(stream(messages), media_type="text/event-stream")


@app.post("/course")
async def add_course(course : model.Course):
    ner =  await course_extraction(course.course_detail , "gpt-4.1-mini")
    status = await import_course(ner , course.name , course.link)
    return status

def _write_file(path: str, content: bytes):
    with open(path, "wb") as f:
        f.write(content)

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
    await asyncio.get_event_loop().run_in_executor(None, _write_file, save_path, content)

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
    
@app.post("/clear")
async def clear_data():
    keep = []
    es = await connect()
    indices = list((await es.indices.get_alias(index="*")).keys())
    for index in indices:
        await es.indices.delete(index=index)
        keep.append(f"Deleted index: {index}")
    return {"deleted_indices": keep}

@app.post("/push_movie_data")
async def update_index():
    status1 = await moive_to_db()
    status2 = await embedding_to_chroma()
    return {"message": f"Index updated successfully. {''} / {status2}"}


@app.post("/rerank")
async def rerank(query: str):
    search = await hybrid_search(query)
 
    return search



# from elasticsearch import Elasticsearchmo

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



