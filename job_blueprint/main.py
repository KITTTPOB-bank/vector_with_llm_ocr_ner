from fastapi import FastAPI, File, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from agent import chat
import os
from libs.extraction import spacy_extraction, llm_extraction
from libs.convect import pdf_to_markdown , pdf_to_markdown_EasyOCR , pdf_to_markdown_MistralOCR , any_to_markdown
from database.handler import import_skil
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def stream_openai(messages: list):
    tools = []
    async for message in chat.call_agent(tools).astream_events({"messages" : messages, "review": []}, version="v2"):
        if message["event"] == "on_chat_model_stream":
            if message["metadata"]["langgraph_node"] == "node_model":
                if message["data"]['chunk'].content:
                    yield message["data"]['chunk'].content



@app.get("/chat/stream")
async def chat_stream():
    async def fake_stream():
        for word in ["Hello", "from", "stream", "!"]:
            yield word + " "
    return StreamingResponse(fake_stream(), media_type="text/plain")


 
@app.post("/extract")
async def extract_text(
    file: UploadFile = File(...),
    read_by: str = Form("default")
):
    SAVE_DIR = "./files"
    os.makedirs(SAVE_DIR, exist_ok=True)  
    
    filename  = file.filename
    save_path = os.path.join(SAVE_DIR, filename)

    if os.path.exists(save_path):
        raise HTTPException(
            status_code=400,
            detail=f"ไฟล์ '{filename}' มีอยู่แล้วในระบบ"
        )


    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)


    if read_by == "default" and filename.endswith(".pdf"):
        read_by = "pdf"

    match read_by:
        case "default":
            markdown = any_to_markdown(save_path)
        case "pdf":
            markdown = pdf_to_markdown(save_path)
        case "mistral":
            markdown = pdf_to_markdown_MistralOCR(save_path)
        case "easy":
            markdown = pdf_to_markdown_EasyOCR(content)
        case _:
            raise HTTPException(status_code=400, detail="Invalid OCR type. Choose: default, easy, mistral")
        
    if len(markdown) < 100:
        raise HTTPException(
            status_code=400,
            detail="ไม่สามารถสกัดเอกสารได้ ลองใช้เป็น `mistral`"
        )

    try:
        ner = spacy_extraction(markdown)
        blueprint = llm_extraction(ner, markdown, "gpt-4.1-mini")

        status = import_skil(blueprint)

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
