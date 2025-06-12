# หัวข้อที่มี
1. โครงสร้าง Project
2. วิธีการติดตั้ง 
3. ทดสอบการทำงาน
4. system overview
5. สำหรับติดตั้งภายในเครื่อง
   
# โครงสร้าง Project
 ```
. backend
├── files/                        # PDF Resume ที่ต้องการประมวลผล (นำเข้าไฟล์เป็น mockup หรือใช้ที่มีอยู่ได้คับ)
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


### 4. การเพิ่ม resume

#### ตัวอย่าง (เพิ่มเติม esayocr ต้องโหลดโมเดลครั้งแรกใช้เวลานาน สามารถปรับภาษาใน convect.py)
![image](https://github.com/user-attachments/assets/e6dfdefd-b173-4f99-8f0f-3ea8cc17beef)

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
### เทคนิคการค้นหา
1. ใช้ Hybrid search โดยแบ่งเป็น 1. Chroma vector search -> 3 chunk 2. elastic keyword search -> 3 rows หรือ 50%/50%
2. จากนั้นนำมา รวมกันและทำกระบวนส่ง ข้อมูล, คำค้นหา -> ไปยังกระบวนการ rerank ผ่าน Cohere rerank 3.5 model โดยจะได้ คะแนน และข้อมูล 3 ตำแหน่งที่มีความใกล้เคียงกับคำค้นหาที่สุด
3. ส่งคืนผลลัพธ์
### การนำ llm มาประยุกต์ใช้
1. ทำให้ เทคนิคการค้นหาเป็นเครื่องมือหนึ่งไว้ให้ llm  (hybrid search tool)
2. เมื่อผู้ใช่สงคำถาม llm จะวิเคราะห์ และสกัด keyword เป็นภาษาอังฤษ จากนั้นทำ toolcalling -> hybrid search tool
3. ได้รับผลลัพธ์มาตอบให้กับผู้ใช้

## ระบบจัด แนะนำคอร์สเรียน ทักษะ Job Blue Print 
### ขั้นตอนการนำเข้าข้อมูล resume 
1. แปลง file pdf หรือไฟล์อื่นๆ เช่น docx เป็น markdown โดยมี 3 วิธี คือ
    1. docling with DoclingParseV4DocumentBackend  # แนะนำ ไม่ช้าจนเกินไป
    2. docling with EasyOcr # ช้าแต่ใช้ในกรณี DoclingParseV4DocumentBackend แปลงข้อมูลไม่ได้ 
    ``` ครั้งแรกที่ใช้จะทำการ pull model จะใช้เวลานาน ```
    3. MistralOCR # แม่นยำสุดแต่มีค่าใช้จ่าย
2. สกัดข้อมูล markdown โดยใช้ spacy-llm สกัด ทักษะลงใน -> skill list
3. ส่ง skill list , markdown ไปยัง llm เพื่อสกัดข้อมูลอีกครั้งในโครงสร้าง
   ```
   class SkillExperience(BaseModel):
    skill: list[str]  
    year: int  
    position: str 

   class ResumeExtraction(BaseModel):
    skills_by_position: list[SkillExperience] 
    job_title: str
    
   ```
4. เก็บข้อมูลเข้า elastic database
### ขั้นตอนการนำเข้าข้อมูล course 
1. รับข้อมูลผู้ใช้ แปลงเป็น skill list โดยใช้ llm
### ขั้นตอนการค้นหาข้อมูล
1. ใช้ระบบ ai agent รับ msg ผู้ใช้ และใช้เครื่องมือ mapping ข้อมูล resume และ course
2. มีเครื่องมือ ดังนี้
   1. job_blueprint โดยจะทำการ summarize ข้อมูลทั้งหมด โดยผู้ใช้สามารถส่ง ตำแหน่งที่สนใจเพื่อทำกระบวนการได้
   2. popular_field_by_year จะเป็นเครื่องมือ 'skill', 'position'  (ตำแหน่ง), 'desired_job' (งานที่ยื่น) ดูรายการ ที่มีจำนวนเยอะสุดต่อ ปี เช่น ทักษะไหนที่ปีนี้ นิยมสุด หรือ งานที่คนทั่วไปยื่น ปีที่แล้ว งานอะไรนิยมสุด อนาคต สามารถพัฒนาให้เน้นไปเฉพาะสายงานได้
   3. search_courses_by_skills ค้นหา course จากทักษะที่ต้องการ โดยจะเรียงคอร์สที่มีทักษะตรงมากที่สุดให้กับผู้ใช้
   4. recommend_skill_for_position แนะนำ ทักษะ จากตำแหน่งที่ระบุ
3. ai agent ตีความ messages จากนั้น ส่งคืน ผลลัพธ์ให้กับผู้ใช้
4. เพิ่มเติม หากข้อความมากเกิน 15 conversation จะทำการสรุปส่วนที่เกิน เป็นสรุปการพูดคุยทีผ่านมา และส่งไปพร้อมกับ messages ปัจจุบัน



# สำหรับติดตั้งภายในเครื่อง
```
python 3.11

cd backend

python -m venv skl-project
skl-project\Scripts\activate
pip install -r .\requirements.txt

[$ docker run -d --name elasticsearch --net somenetwork -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:tag
](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic)

es = AsyncElasticsearch("http://localhost:9200")***

pystart.py

uvicorn main:app --host=0.0.0.0 --port=8000


cd frontend

npm i
npm run start
```
