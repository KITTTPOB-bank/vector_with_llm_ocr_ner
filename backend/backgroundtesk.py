# from fastapi import FastAPI, File, HTTPException, UploadFile, Form, BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# from agent import chat
# import os
# import uuid

# from libs.extraction import spacy_extraction, llm_extraction
# from libs.convect import pdf_to_markdown , pdf_to_markdown_EasyOCR , pdf_to_markdown_MistralOCR , any_to_markdown
# from database.handler import import_skil
# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# async def stream_openai(messages: list):
#     tools = []
#     async for message in chat.call_agent(tools).astream_events({"messages" : messages, "review": []}, version="v2"):
#         if message["event"] == "on_chat_model_stream":
#             if message["metadata"]["langgraph_node"] == "node_model":
#                 if message["data"]['chunk'].content:
#                     yield message["data"]['chunk'].content



# @app.get("/chat/stream")
# async def chat_stream():
#     async def fake_stream():
#         for word in ["Hello", "from", "stream", "!"]:
#             yield word + " "
#     return StreamingResponse(fake_stream(), media_type="text/plain")



# def full_pipeline(save_path: str, content: bytes, read_by: str, status_path: str):
#     try:
#         match read_by:
#             case "default":
#                 markdown = any_to_markdown(save_path)
#             case "pdf":
#                 markdown = pdf_to_markdown(save_path)
#             case "mistral":
#                 markdown = pdf_to_markdown_MistralOCR(save_path)
#             case "easy":
#                 markdown = pdf_to_markdown_EasyOCR(content)
#             case _:
#                 raise Exception("Invalid OCR type")

#         if len(markdown.strip()) < 100:
#             raise Exception("OCR สกัดข้อความได้น้อยเกินไป")

#         ner = spacy_extraction(markdown)
#         blueprint = llm_extraction(ner, markdown, "gpt-4.1-mini")
#         import_skil(blueprint)

#         with open(status_path, "w") as f:
#             f.write("success")

#     except Exception as e:
#         with open(status_path, "w") as f:
#             f.write(f"error: {str(e)}")

# @app.post("/extract")
# async def extract_text(
#     background_tasks: BackgroundTasks,
#     file: UploadFile = File(...),
#     read_by: str = Form("default")
# ):
#     SAVE_DIR = "./files"
#     STATUS_DIR = "./status"
#     os.makedirs(SAVE_DIR, exist_ok=True)
#     os.makedirs(STATUS_DIR, exist_ok=True)

#     filename = file.filename
#     file_id = str(uuid.uuid4()) 
#     save_path = os.path.join(SAVE_DIR, f"{file_id}_{filename}")
#     status_path = os.path.join(STATUS_DIR, f"{file_id}.txt")

#     content = await file.read()
#     with open(save_path, "wb") as f:
#         f.write(content)

#     if read_by == "default" and filename.lower().endswith(".pdf"):
#         read_by = "pdf"

#     background_tasks.add_task(full_pipeline, save_path, content, read_by, status_path)

#     return {"status": "processing", "file_id": file_id}
   
# @app.get("/status/{file_id}")
# async def get_status(file_id: str):
#     status_path = os.path.join("./status", f"{file_id}.txt")
    
#     if not os.path.exists(status_path):
#         return {"status": "not_found"}

#     with open(status_path, "r") as f:
#         content = f.read()

#     if content == "success":
#         return {"status": "success"}
#     elif content.startswith("error:"):
#         return {"status": "error", "detail": content[6:].strip()}
#     else:
#         return {"status": "processing"}

# # from elasticsearch import Elasticsearch

# # es = Elasticsearch("http://localhost:9200")

# # query = {
# #     "size": 0,
# #     "query": {
# #         "match_phrase": {
# #             "position": "Fullstack Developer"
# #         }
# #     },
# #     "aggs": {
# #         "popular_skills": {
# #             "terms": {
# #                 "field": "skill.keyword",
# #                 "size": 10
# #             }
# #         }
# #     }
# # }

# # response = es.search(index="skills_by_position", body=query)

# # # แสดงผลสกิลที่นิยมที่สุด
# # for bucket in response['aggregations']['popular_skills']['buckets']:
# #     print(f"Skill: {bucket['key']}, Count: {bucket['doc_count']}")



# from elasticsearch import Elasticsearch

# es = Elasticsearch("http://localhost:9200")

# # ดึงชื่อ index ทั้งหมด
# indices = es.indices.get_alias(index="*").keys()

# # ลบ index ทุกตัว
# for index in indices:
#     es.indices.delete(index=index)
#     print(f"Deleted index: {index}")
