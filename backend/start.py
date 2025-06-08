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
},
{
    "name" : "เขียนโปรแกรมภาษา Visual Basic .NET กับ SQL Server โดยใช้ Entity Framework 6",
    "link" : "https://www.skilllane.com/courses/vb-net-sql-server-entity-framework",
    "course_detail": """
        สอนเขียนโปรแกรมด้วยภาษา Visual Basic, .NET ให้คุณทำเป็นได้อย่างรวดเร็ว สามารถสร้างโปรแกรมขึ้นมาใช้งานได้เลยหลังจากเรียนจบ เพื่อเพิ่มทักษะ .NET

        ประโยชน์ที่ผู้เรียนจะได้รับ
        - สามารถเขียนโปรแกรมด้วยภาษา Visual Basic, .NET ได้อย่างรวดเร็ว
        - สามารถใช้ Entity Framework เชื่อมต่อฐานข้อมูล SQL Server แบบ Database First ได้
        - สามารถเขียนคำสั่ง LINQ to Entities เพื่อจัดการฐานข้อมูล SQL Server ได้
        - สามารถประยุกต์ใช้งาน CRUD Operation ร่วมกับฐานข้อมูล SQL Server ได้
        - สามารถสร้างโปรแกรม Windows Application ร่วมกับฐานขัอมูล SQL Server ได้อย่างรวดเร็ว        
    """
},
{
    "name" : "เขียน Python พัฒนา AI Machine Vision",
    "link" : "https://www.skilllane.com/courses/python-machine-vision-AI",
    "course_detail": """
        สอนให้ทุกคนมีความรู้ด้านการเขียนภาษา Python บวกกับการใช้งาน Library (OpenCV) ซึ่งถูกสร้างขึ้นมาเพื่อใช้สำหรับการพัฒนา AI Machine Vision โดยเฉพาะ
        ประโยชน์ที่ผู้เรียนจะได้รับ
        - ความรู้ความเข้าใจในหลักการของ Machine Vision
        - ทักษะการเขียนภาษา Python ร่วมกัน Library OpenCV
        - ทักษะการเขียน Code ตรวจจับตำแหน่งต่างๆในภาพ (Detection)
        - ทักษะการประยุกต์และเขียน Code เพื่อพัฒนา AI Machine Vision
    """
}
]

desired_job = ""

async def process_pdf(file_path):
    print(f"Processing PDF: {file_path} ...")
    markdown = await pdf_to_markdown(file_path)
    ner = await spacy_extraction(markdown)
    blueprint = await llm_extraction(ner, markdown, "gpt-4.1-mini")
    status = await import_skil(blueprint, desired_job)
    print(f"Finished PDF: {file_path} with status: {status}")

async def process_course(course):
    print(f"Processing course: {course['name']} ...")
    ner = await course_extraction(course['course_detail'], "gpt-4.1-mini")
    status = await import_course(ner, course['name'], course['link'])
    print(f"Finished course: {course['name']} with status: {status}")

async def main():
    print("GET START ......")

    # 1. อ่าน PDF ทีละไฟล์
    folder = Path("files")
    pdf_files = sorted(folder.glob("*.pdf")) 
    for pdf_file in pdf_files:
        await process_pdf(pdf_file)

    # 2. ย้ายข้อมูลเข้า DB
    await moive_to_db()
    print("success moive_to_db")

    # 3. ฝัง Embedding
    await embedding_to_chroma()
    print("success embedding_to_chroma")

    # 4. ประมวลผลคอร์สทีละรายการ
    for c in course:
        await process_course(c)

    print("success all task")

if __name__ == "__main__":
    asyncio.run(main())