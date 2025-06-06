from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/chat/stream")
async def chat_stream():
    async def fake_stream():
        for word in ["Hello", "from", "stream", "!"]:
            yield word + " "
    return StreamingResponse(fake_stream(), media_type="text/plain")

@app.post("/extract")
async def extract_text(
    file: UploadFile = File(...),
    ocr_type: str = Form("default")  
):
    content = await file.read()

    return content

    # if ocr_type == "default":
    #     markdown = file_to_markdown(content)
    # elif ocr_type == "easy":
    #     markdown = pdf_to_markdown_EasyOCR(content)
    # elif ocr_type == "mistral":
    #     markdown = pdf_to_markdown_MistralOCR(content)
    # else:
    #     raise HTTPException(status_code=400, detail="Invalid OCR type. Choose: default, easy, mistral")

    # return PlainTextResponse(markdown)
