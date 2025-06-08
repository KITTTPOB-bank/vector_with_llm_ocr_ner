// App.tsx
import React, { useEffect, useRef, useState } from "react";
import { Button, Input, Spin, Space, Modal, Radio, RadioChangeEvent, Upload } from "antd";
import { ArrowUpOutlined, LoadingOutlined } from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./index.css";
import { UploadOutlined } from '@ant-design/icons';
import type { UploadChangeParam, UploadFile } from 'antd/es/upload';

const antIcon = <LoadingOutlined style={{ fontSize: 24, color: "white" }} spin />;

type Message = {
  role: "user" | "ai";
  content: string;
};

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [mode, setMode] = useState<"job" | "movie">("job");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isModalOpentwo, setIsModalOpentwo] = useState(false);
  const [selectedOption, setSelectedOption] = useState("default");
  const [fileList, setFileList] = useState<UploadFile<any>[]>([]);
  const [loading, setLoading] = useState(false);
  const [course, setCourse] = useState({
    name: "",
    link: "",
    course_detail: "",
  });
  const onChange = (e: RadioChangeEvent) => {
    setSelectedOption(e.target.value);
  };
 
  const showModal = () => {
    setIsModalOpen(true);
  };

  const showModalTwo = () => {
    setIsModalOpentwo(true);
  };

  const handleCancelTwo = () => {
    setIsModalOpentwo(false);
  };
  const handleUploadChange = (info: UploadChangeParam) => {
    setFileList(info.fileList);
  };

  const handleOk = async (selectedOption: string, upload: UploadFile[]) => {
    if (upload.length === 0) {
      alert("กรุณาเลือกไฟล์ก่อน");
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append("file", upload[0].originFileObj as Blob);
    formData.append("read_by", selectedOption);
    formData.append("desired_job", "");
    try {
      const res = await fetch("http://localhost:8000/extract", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "อัปโหลดไม่สำเร็จ");
      }

      alert(`${data.message} (จำนวน: ${data.indexed_count} รายการ)`);
      setIsModalOpen(false);
      setFileList([]);
    } catch (err: any) {
      console.error("Error:", err);
      alert(`เกิดข้อผิดพลาด: ${err.message}`);
    }
    setLoading(false);
  };
  const handleOkTwo = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/course", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(course),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "ส่งข้อมูลไม่สำเร็จ");
      }

      alert(data.message);
      setIsModalOpentwo(false);
      setCourse({ name: "", link: "", course_detail: "" });
    } catch (err: any) {
      console.error("Error:", err);
      alert(`เกิดข้อผิดพลาด: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setIsModalOpen(false);
  };
  const handleSend = async () => {
    if (!inputText.trim()) return;

    const newMessages: Message[] = [...messages, { role: "user", content: inputText }, { role: "ai", content: "..." }];
    setMessages(newMessages);
    setInputText("");
    setStreaming(true);
    let url = "http://localhost:8000/chatJob"
    if (mode == "job") {
      url = "http://localhost:8000/chatJob";
    }
    else {
      url = "http://localhost:8000/chatMovie";
    }
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: [...messages, { role: "user", content: inputText }] }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      const read = async () => {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunkStr = decoder.decode(value, { stream: true });
          console.log(chunkStr)
          buffer += chunkStr || "";
          setMessages((prev) =>
            prev.map((m, i) =>
              i === prev.length - 1 ? { ...m, content: buffer } : m
            )
          );
        }
        setStreaming(false);
      };

      read();
    } catch (err) {
      console.error("Stream error:", err);
      setStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && !streaming) {
      e.preventDefault();
      handleSend();
    }
  };


  //  ? "bg-gray-200 text-gray text-right"
  //         : "text-gray-800 text-left" bg-gray-100
  return (
    <div className="min-h-screen bg-gray-200 text-black p-4 flex flex-col items-center">
      <div className="w-full max-w-2xl flex-1 overflow-auto space-y-2 rounded-lg p-3">

        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`
          whitespace-pre-wrap px-4 py-2 rounded-xl mb-2 inline-block max-w-[80%]
          ${msg.role === "user" ? "bg-white text-right" : "bg-transparent text-left"}
        `}
            >
              {msg.role === "ai" && msg.content === "..." ? (
                <Spin indicator={antIcon} />
              ) : (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="w-full max-w-3xl mt-4 flex items-end gap-2">

        <Space>
          <Button
            type={mode === "job" ? "primary" : "default"}
            onClick={() => setMode("job")}
          >
            Job
          </Button>
          <Button
            type={mode === "movie" ? "primary" : "default"}
            onClick={() => setMode("movie")}
          >
            Movie
          </Button>
          <Button variant="solid" icon={<UploadOutlined />} color="cyan" onClick={showModal}>
            Resume
          </Button>

          <Button variant="solid" icon={<UploadOutlined />} color="cyan" onClick={showModalTwo}>
            Course
          </Button>
        </Space>

        <Input.TextArea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={streaming}
          className="flex-1"
        />

        <Button
          type="primary"
          icon={<ArrowUpOutlined />}
          onClick={handleSend}
          disabled={streaming}
        />
      </div>



      <Modal
        title="ส่งข้อมูลคอร์ส"
        open={isModalOpentwo}
        onOk={handleOkTwo}
        onCancel={handleCancelTwo}
        confirmLoading={loading}
      >
        <Input
          placeholder="ชื่อคอร์ส"
          value={course.name}
          onChange={(e) => setCourse({ ...course, name: e.target.value })}
          className="mb-2"
        />
        <Input
          placeholder="ลิงก์"
          value={course.link}
          onChange={(e) => setCourse({ ...course, link: e.target.value })}
          className="mb-2"
        />
        <Input.TextArea
          rows={5}
          placeholder="รายละเอียดคอร์ส"
          value={course.course_detail}
          onChange={(e) => setCourse({ ...course, course_detail: e.target.value })}
        />
      </Modal>

      <Modal
        title="เลือกวิธีการสกัดข้อมูลจากไฟล์"
        open={isModalOpen}
        onOk={() => handleOk(selectedOption, fileList)}
        onCancel={handleCancel}
        confirmLoading={loading}
      >
        <Radio.Group
          onChange={onChange}
          value={selectedOption}
          style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}
        >
          <Radio value="default">สกัดข้อมูลแบบทั่วไป (แนะนำ)</Radio>
          <Radio value="easy">สกัดข้อมูล โดย EasyOCR</Radio>
          <Radio value="mistral">
            สกัดข้อมูล โดย Mistral-OCR (มีค่าใช้จ่าย 1000 หน้า ต่อ 1 ดอลลาร์)
          </Radio>
        </Radio.Group>

        <Radio.Group
          onChange={onChange}
          value={selectedOption}
          style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}
        >

        </Radio.Group>

        <Upload
          beforeUpload={() => false}
          onChange={handleUploadChange}
          fileList={fileList}
          maxCount={1}
          style={{ marginTop: 16 }}
        >
          <Button>เลือกไฟล์</Button>
        </Upload>
      </Modal>
    </div>
  );
}
export default App;
