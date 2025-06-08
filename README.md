# โครงสร้าง Project
 ```
. backend
├── files/                         # PDF Resume ที่ต้องการประมวลผล
│
├── libs/                         # ไลบรารีหลักสำหรับการประมวลผล
│   ├── config.cfg                # ค่าคอนฟิกของระบบ spacy-llm
│   ├── extraction.py             # โมดูลสำหรับแยกข้อมูลจาก Resume และ Course
│   ├── convect.py                # โมดูลสำหรับแปลง PDF เป็น Markdown หรือ Text
│   └── retrieval.py              # โมดูลสำหรับดึงข้อมูล rag hybrid , agentic rag
│
├── database/                     # ส่วนเชื่อมต่อฐานข้อมูล
│   ├── elastic.py                # เชื่อมต่อและจัดการข้อมูลใน Elasticsearch
│   └── chroma.py                 # ทำ embedding และจัดเก็บใน ChromaDB
│
├── agent/                        
│   └── chat.py                   # โมดูลแชตที่ประสานงานกับโมเดล LLM
│
├── base_model/                   
│   └── model.py                  # pydantic model
│
├── tool/                        
│   └── factory.py                # สร้าง tool ต่าง ๆ ให้ agent ใช้งานได้แบบไดนามิก
│
├── main.py                       # สคริปต์หลักสำหรับการรันระบบ (entry point)
├── start.py                      # สคริปต์เริ่มต้นระบบหรือสำหรับ deployment / mockup data
```

# วิธีการติดตั้ง และทดสอบ 
เพิ่มไฟล .env ใน ลงในโปรเจ็ค
```
. 
├── frontend/                     
├── backend/ 
├── .env (ไว้ตรงนี้)
```

```
MISTRAL_API_KEY = ""
OPENAI_API_KEY=""
COHERE_API_KEY = ""
```
รันคำสั่ง
```
docker-compose up -d --build
```

เข้าไปที่ Containers ของ -> backend 
เลือก open terminal 
รันคำสั่ง เพื่อทำการ mockup data
```
python start.py  
```

![image](https://github.com/user-attachments/assets/b6019d0a-294d-4302-b2e5-62c4e01592a9)
![image](https://github.com/user-attachments/assets/aeaf5b3d-b68b-4e21-8d0f-de75020a678e)

รอจนขึ้น sussecc all task
 
เข้าไปที่ http://localhost:8000/docs
🧪 API Endpoints
Method	Endpoint	Description
```
POST	/chatJob	โต้ตอบกับระบบตามข้อมูล Resume, Course
{
  "role": "user",
  "content": "ทักษะ ยอดฮิต สำหรับ สายงาน Full stack .net"
} 
{
  "role": "ai",
  "content": "...."
}
```
```
POST	/chatMovie	โต้ตอบกับระบบตามข้อมูล Course
POST	/course	เพิ่มคอร์สออนไลน์เข้าสู่ระบบ
POST	/extract	แปลง PDF และดึงข้อมูลจาก Resume
POST	/clear	ล้างข้อมูลทั้งหมดในระบบ
POST	/push_movie_data	อัปเดต Index สำหรับ Course
POST	/rerank	ปรับลำดับความเกี่ยวข้องใหม่
```
