from pydantic import BaseModel, Field

class SkillExperience(BaseModel):
    skill: list[str] = Field(description="List of technical or skills used in the  position.")
    year: int = Field(description="The most recent calendar year the skill(s) were used in that position.")
    position: str = Field(description="The job title or role where the skill(s) were applied (e.g., Software Developer).")

class ResumeExtraction(BaseModel):
    skills_by_position: list[SkillExperience] = Field(description="A list of grouped skills by job position.")
    job_title: str = Field(description="The main or primary job title emphasized or highlighted in the resume. If none found, return empty string.")
    
class CourseExtraction(BaseModel):
    skill: list[str] = Field(description="List of technical or skills.")

class Course(BaseModel):
    name: str = Field(default="สร้าง Real-Time Web App ด้วย Socket.io, Next.js")
    course_detail: str = Field(default="""
    - สามารถเขียนโค้ดด้วยภาษา TypeScript ได้
    - เรียนรู้ Socket.io และ Node.js สำหรับงานแบบ Realtime
    - รู้วิธีสร้าง Dashboard / Chart และแสดงผลข้อมูลแบบ Realtime
    - เรียนรู้การใช้งาน Next.js ล่าสุด ร่วมกับ Socket.io
    - เรียนรู้ Material UI / shadcn/ui ใช้สำหรับสร้าง UI และ Dashboard ร่วมกับ Next.js
    - เรียนรู้ Drizzle ORM และใช้งานร่วมกับฐานข้อมูล MySQL ได้
    - สามารถนำ Socket.io ไปใช้กับ framework อื่นๆ ได้
    - สามารถ Build / Deploy Next.js / Socket.io เพื่อใช้งานบน production ได้
""")
    

class Message(BaseModel):
    role: str  = Field(default="user")
    content: str 

class ChatMessages(BaseModel):
    messages: list[Message] 
