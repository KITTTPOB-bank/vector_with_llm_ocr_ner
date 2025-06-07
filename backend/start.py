import asyncio
from pathlib import Path
from libs.extraction import spacy_extraction, llm_extraction, course_extraction
from libs.convect import pdf_to_markdown
from database.elastic import import_skil, import_course, moive_to_db
from database.chroma import embedding_to_chroma

course = [{
    "name": "สร้าง Real-Time Web App ด้วย Socket.io, Next.js",
    "link": "https://www.skilllane.com/courses/MySQL-Real-time-Web-App",
    "course_detail": """
        - สามารถเขียนโค้ดด้วยภาษา TypeScript ได้
        - เรียนรู้ Socket.io และ Node.js สำหรับงานแบบ Realtime
        - รู้วิธีสร้าง Dashboard / Chart และแสดงผลข้อมูลแบบ Realtime
        - เรียนรู้การใช้งาน Next.js ล่าสุด ร่วมกับ Socket.io
        - เรียนรู้ Material UI / shadcn/ui ใช้สำหรับสร้าง UI และ Dashboard ร่วมกับ Next.js
        - เรียนรู้ Drizzle ORM และใช้งานร่วมกับฐานข้อมูล MySQL ได้
        - สามารถนำ Socket.io ไปใช้กับ framework อื่นๆ ได้
        - สามารถ Build / Deploy Next.js / Socket.io เพื่อใช้งานบน production ได้
    """
},
{
    "name": "Data Analytics ด้วย Python เรียนรู้การวิเคราะห์ข้อมูล",
    "link": "https://www.skilllane.com/courses/data-analytics-with-python",
    "course_detail": """
        หลักสูตร "Data Analytics ด้วย Python เรียนรู้การวิเคราะห์ข้อมูล" นี้เหมาะสำหรับผู้ที่ต้องการพัฒนาทักษะการวิเคราะห์ข้อมูล โดยจะเริ่มต้นจากพื้นฐานและค่อย ๆ
        ขยับขึ้นไปสู่เทคนิคขั้นสูงที่ใช้ในโลกของการวิเคราะห์ธุรกิจ รวมถึงการใช้เครื่องมือ Python ที่ได้รับความนิยมอย่าง Pandas, NumPy, Matplotlib และ Seaborn 
        เพื่อช่วยในการจัดการและแสดงผลข้อมูล
    """
}
]

desired_job = ""
has_worked = False  

async def process_pdf(file_path):
    print(f"Processing PDF: {file_path} ...")
    markdown = await pdf_to_markdown(file_path)
    ner = await spacy_extraction(markdown)
    blueprint = await llm_extraction(ner, markdown, "gpt-4.1-mini")
    status = await import_skil(blueprint, desired_job, has_worked)
    print(f"Finished PDF: {file_path} with status: {status}")

async def process_course(course):
    print(f"Processing course: {course['name']} ...")
    ner = await course_extraction(course['course_detail'], "gpt-4.1-mini")
    status = await import_course(ner, course['name'], course['link'])
    print(f"Finished course: {course['name']} with status: {status}")

async def main():
    print("GET START ......")
    folder = Path("files")
    pdf_files = folder.glob("*.pdf")
    for pdf_file in pdf_files:
        await process_pdf(pdf_file)
    await moive_to_db()
    print("sussecc moive_to_db")
    await embedding_to_chroma()
    print("sussecc embedding_to_chroma")
    for c in course:
        await process_course(c)
    print("sussecc all task")

if __name__ == "__main__":
    asyncio.run(main())
