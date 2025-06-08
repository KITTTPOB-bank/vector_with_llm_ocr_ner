![image](https://github.com/user-attachments/assets/7a285174-483c-44b7-8ec9-bf16aceb2350)# หัวข้อที่มี
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

หากเกิดข้อผิดพลาด
```
pip._vendor.urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out. container มีขนาด 9 gb
ลองทำ docker-compose up -d --build
```

เข้าไปที่ Containers ของ -> backend 
เลือก open terminal 
รันคำสั่ง เพื่อทำการ mockup data
```
python start.py  
```

![image](https://github.com/user-attachments/assets/b6019d0a-294d-4302-b2e5-62c4e01592a9)

![image](https://github.com/user-attachments/assets/c3c917c1-e622-4a8e-bd85-f2316874b955)

![image](https://github.com/user-attachments/assets/548b2071-4ac3-4749-9760-ba1d0869ef3f)

รอจนขึ้น sussecc all task


# ทดสอบการทำงาน
## หน้าบ้าน
### 1. การแชทพูดคุย หนัง

#### ตัวอย่างการถาม
![image](https://github.com/user-attachments/assets/bfa81673-d230-4df4-9810-1778130ffc68)

#### log การค้นหา
![image](https://github.com/user-attachments/assets/b982b9e7-ac01-4727-9608-00c5771e4b74)


### 2. การแชทพูดคุย เกี่ยวกับงาน ทักษะ คอร์ส

#### ตัวอย่างการถาม การแนะนำคอสเรียน
![image](https://github.com/user-attachments/assets/f5eeb7b8-bcb2-4e2f-b889-e1bc19366a3d)

#### 

#### log การค้นหา
![image](https://github.com/user-attachments/assets/082a3253-de82-45f5-8fae-adecb5861b65)


### 3. การทำ Job blue print

#### ตัวอย่าง
![image](https://github.com/user-attachments/assets/7c22aa76-b70f-4a63-854a-f82040bed4ef)


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

## database
```
http://localhost:9200/movie/_search?pretty ## movie
http://localhost:9200/resumes/_search?pretty ## resumes
http://localhost:9200/courses/_search?pretty ## courses
```
# system overview

## ระบบค้นหาหนังโดยผสมผสาน Traditional Search และ Generative AI 
### ขั้นตอนการนำเข้า (ทำในกระบวนการ python start.py)
1. แปลงข้อมูลรูปแบบ csv -> pandas 
2. ทำการ Embeddings แต่ละแถว ของ pandas  
3. นำข้อมูล vector ที่แปลงจาก ข้อ 2 เก็บเข้า Chroma ใน chroma_langchain_db
4. นำข้อมูล document ที่ได้จากการแปลงเป็น pandas เก็บเข้า elastic db
### ขั้นตอนการค้นหา



