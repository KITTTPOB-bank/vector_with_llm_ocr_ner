📄 Resume Skill Extractor & Course Analyzer
ระบบที่ช่วยวิเคราะห์ Resume และ Online Courses เพื่อแยกและจัดเก็บ ทักษะ อย่างมีโครงสร้าง พร้อมรองรับการค้นหาและปรับแต่งผลลัพธ์โดยใช้เทคโนโลยี NLP และ Embedding

🔧 Features
✅ แปลงไฟล์ PDF เป็น Markdown เพื่อเตรียมข้อมูลให้ LLM วิเคราะห์ โดยใช้ docling

.
├── files/                     # PDF Resume ที่ต้องการประมวลผล
├── libs/
│   ├── extraction.py          # แยกข้อมูลจาก Resume / Course
│   └── convect.py             # แปลง PDF เป็น Markdown
├── database/
│   ├── elastic.py             # เชื่อมต่อและบันทึกข้อมูลใน Elasticsearch
│   └── chroma.py              # ทำ embedding และบันทึกใน ChromaDB
├── main.py                    # สคริปต์หลักในการประมวลผล



# วิธีการติดตั้ง และทดสอบ 
## 1. 
เพิ่มไฟล .env ใน โฟลเดอร์ backend
```
MISTRAL_API_KEY = ""
OPENAI_API_KEY=""
COHERE_API_KEY = ""
```
รันคำสั่ง
```
docker-compose up -d --build
```
เข้าไปที่ Containers ของ backend -> backend 
เลือก open terminal 
รันคำสั่ง 
```
python start.py 
```
![image](https://github.com/user-attachments/assets/b6019d0a-294d-4302-b2e5-62c4e01592a9)
![image](https://github.com/user-attachments/assets/aeaf5b3d-b68b-4e21-8d0f-de75020a678e)

รอจนขึ้น sussecc all task 

## 2. 
เข้าไปที่ http://localhost:8000/docs
🧪 API Endpoints
Method	Endpoint	Description
POST	/chatJob	โต้ตอบกับระบบตามข้อมูล Resume, Course
{
  "role": "user",
  "content": "ทักษะ ยอดฮิต สำหรับ สายงาน Full stack .net"
} 
{
  "role": "ai",
  "content": "...."
} 

POST	/chatMovie	โต้ตอบกับระบบตามข้อมูล Course


POST	/course	เพิ่มคอร์สออนไลน์เข้าสู่ระบบ
POST	/extract	แปลง PDF และดึงข้อมูลจาก Resume
POST	/clear	ล้างข้อมูลทั้งหมดในระบบ
POST	/push_movie_data	อัปเดต Index สำหรับ Course
POST	/rerank	ปรับลำดับความเกี่ยวข้องใหม่
