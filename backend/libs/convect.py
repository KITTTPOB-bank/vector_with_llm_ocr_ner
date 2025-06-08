import warnings
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions
from mistralai import Mistral
import os
import base64
from dotenv import load_dotenv
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
import urllib3, socket
from urllib3.connection import HTTPConnection

HTTPConnection.default_socket_options = ( 
    HTTPConnection.default_socket_options + [
    (socket.SOL_SOCKET, socket.SO_SNDBUF, 2000000), 
    (socket.SOL_SOCKET, socket.SO_RCVBUF, 2000000)
    ])
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
warnings.filterwarnings("ignore", category=UserWarning)

async def encode_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')
    except Exception as e:  
        return None


async def pdf_to_markdown(source: str) -> str:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = False

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=DoclingParseV4DocumentBackend
            )
        }
    )
    doc = doc_converter.convert(source)
    return doc.document.export_to_markdown()

async def any_to_markdown(source) -> str:
    converter = DocumentConverter()
    result = converter.convert(source)
    return result.document.export_to_markdown()


async def pdf_to_markdown_EasyOCR(source : str) -> str:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'model'))

    os.makedirs(model_path, exist_ok=True)

    pipeline_options.ocr_options = EasyOcrOptions(
        lang=["en", "th"],
        force_full_page_ocr=True,
        use_gpu=False,
        model_storage_directory=model_path,
        download_enabled=True,  
    )
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(   
                pipeline_options=pipeline_options,
            )
        }
    )
    doc = converter.convert(source).document
    md = doc.export_to_markdown()

    return md

# ค่าใช้จ่าย Mistral OCR 1 ดอลลาร์ต่อ 1000 หน้า
async def pdf_to_markdown_MistralOCR(source : str) -> str:
    client = Mistral(api_key=MISTRAL_API_KEY)
    base64_pdf = await encode_pdf(source)
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}" 
        },
        include_image_base64=True
    )
    return  ocr_response.pages[0].markdown



 

 
 
 