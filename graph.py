import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    dataset_path: str | None
    insights: Annotated[list[str], operator.add]

@tool
def get_basic_stats(dataset_path: str) -> dict:
    """读取数据集，返回基础统计（模拟大数据处理）"""
    print(f"🛠️ [Tool] 正在分析大数据文件: {dataset_path}")
    # 这里后面我们会换成真实 Polars/Parquet 分片高并发处理
    return {"row_count": 1250000, "mean": 156.7, "max": 9999, "min": 0.5}

tools = [get_basic_stats]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

def planner_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState):
    last_message = state["messages"][-1]
    results = []
    for tool_call in last_message.tool_calls:
        if tool_call["name"] == "get_basic_stats":
            result = get_basic_stats.invoke(tool_call["args"])
            results.append(str(result))
    return {"messages": [AIMessage(content="\n".join(results))]}

def reflector_node(state: AgentState):
    response = llm.invoke([HumanMessage(content="根据工具结果生成3条专业大数据分析洞察（中文）"), *state["messages"]])
    return {"messages": [response], "insights": ["洞察1", "洞察2", "洞察3"]}

def should_continue(state: AgentState) -> Literal["tools", "reflector"]:
    last = state["messages"][-1]
    if last.tool_calls:
        return "tools"
    return "reflector"

workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("tools", tool_node)
workflow.add_node("reflector", reflector_node)

workflow.add_edge(START, "planner")
workflow.add_conditional_edges("planner", should_continue, {"tools": "tools", "reflector": "reflector"})
workflow.add_edge("tools", "planner")
workflow.add_edge("reflector", END)

app = workflow.compile()