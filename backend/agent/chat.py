from typing import TypedDict, Annotated
from langchain_core.messages import ToolMessage,   AIMessage
import os 
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.tools import StructuredTool
load_dotenv()
 
class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_agent(tools : list[StructuredTool]):
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    
    llm = ChatOpenAI(model="gpt-4.1-mini", stream_usage= True, temperature=0 , top_p=0, api_key=OPENAI_KEY)

    async def call_tools(state: State):
        result = []
        tools_by_name = {tool.name: tool for tool in tools}

        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = await tool.ainvoke(tool_call["args"])
            result.append(
                ToolMessage(
                    content=observation,
                    tools_by_name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                )
            )
        return {"messages": result}

    async def should_continue(state: State):
        messages = state["messages"]
        last_message : AIMessage = messages[-1]
        if last_message.tool_calls:
            return "node_tool"
        return "__end__"


    async def call_model(state : State):
        messages = state["messages"]
        print(messages[-1].content)
        model =  llm.bind_tools(tools)
        message = await model.ainvoke(messages)

        print(message)
        return {"messages": [message]}


    workflow = StateGraph(State)
    workflow.add_node("node_model", call_model)
    workflow.add_node("node_tool", call_tools)
    workflow.add_edge("__start__", "node_model")
    workflow.add_conditional_edges(
        "node_model",
        should_continue
    )
    workflow.add_edge("node_tool", "node_model")
         
    return workflow.compile()
