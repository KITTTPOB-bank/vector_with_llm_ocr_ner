# หัวข้อที่มี
1. โครงสร้าง Project
2. วิธีการติดตั้ง 
3. ทดสอบการทำงาน
4. system overview

# โครงสร้าง Project
 ```
. backend
├── files/                        # PDF Resume ที่ต้องการประมวลผล
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

# วิธีการติดตั้ง 
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


# ทดสอบการทำงาน
## หน้าบ้าน


## หลังบ้าน
เข้าไปที่ http://localhost:8000/docs
🧪 API Endpoints
Method	Endpoint	Description

POST	/chatJob	โต้ตอบกับระบบตามข้อมูล Resume, Course

```
[
 {
   "role": "user",
   "content": "ทักษะ ยอดฮิต สำหรับ สายงาน Full stack .net"
 } 
]
หากต้องการส่ง massage ต่อไปๆ ก็ใช้
[
 {
   "role": "user",
   "content": "ทักษะ ยอดฮิต สำหรับ สายงาน Full stack .net"
 },
 {
   "role": "ai",
   "content": "....."
 },
 {
   "role": "user",
   "content": "ขอ Blue Print ของ Full stack .net"
 }
]
```

POST	/chatMovie	โต้ตอบกับระบบตามข้อมูล Course -> ใช้รูปแบบเดียวกันกับ chatJob
```
[
 {
   "role": "user",
   "content": "หนัง แนวดราม่า ที่มีความแอคชั่นหน่อยๆ แนะนำหน่อยคับ"
 } 
]
```
```
POST	/course                # เพิ่มคอร์สออนไลน์เข้าสู่ระบบ 
POST	/extract	              # แปลง PDF และดึงข้อมูลจาก Resume
POST	/clear	                # ล้างข้อมูลทั้งหมด ใน elastic database 
POST	/push_movie_data	      # เพิ่ม และนำข้อมูลลงใน vector/elastic database (ทำการเพิ่มแล้วในขั้นตอนรัน start.py)
POST	/rerank	               # สำหรับทดสอบ hybrid search
```

