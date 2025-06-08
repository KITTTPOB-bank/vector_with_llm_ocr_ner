// App.tsx
import React, { useEffect, useRef, useState } from "react";
import { Button, Input, Spin , Space } from "antd";
import { ArrowUpOutlined, LoadingOutlined } from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./index.css"; 

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

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const newMessages: Message[] = [...messages, { role: "user", content: inputText }, { role: "ai", content: "..." }];
    setMessages(newMessages);
    setInputText("");
    setStreaming(true);
    let url = "http://localhost:8000/chatJob"
    if (mode == "job"){
      url = "http://localhost:8000/chatJob";
    }
    else{
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

      <div className="w-full max-w-2xl mt-4 flex items-end gap-2">

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
    </div>
  );
}
export default App;
