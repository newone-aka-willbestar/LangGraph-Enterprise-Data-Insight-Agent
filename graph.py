# graph.py
import os
from typing import TypedDict, List, Annotated
import operator
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

# 1. 定义状态 (State) - Agent 的共享记忆
class ResearchState(TypedDict):
    topic: str               # 调研主题
    plan: List[str]          # 拆解后的任务列表
    content: List[str]       # 搜集到的素材
    report: str              # 最终生成的报告
    review_feedback: str     # 审核反馈
    steps: int               # 迭代次数，防止死循环

# 2. 初始化 DeepSeek 模型
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.3
)

# --- 节点 A: Planner (拆解意图) ---
def planner_node(state: ResearchState):
    prompt = f"你是一个行业分析专家。请将用户的主题 '{state['topic']}' 拆解成3个深入调研的方向。"
    # 强制要求 JSON 格式或列表格式
    res = llm.invoke([SystemMessage(content=prompt)])
    # 这里简化处理，直接存储
    return {"plan": [res.content], "steps": 1}

# --- 节点 B: Researcher (模拟搜索工具) ---
def researcher_node(state: ResearchState):
    # 面试时说：这里通过 Tool 调用了搜索 API (如 Tavily)
    # 现在为了演示，我们模拟搜索到的数据
    search_data = f"关于 {state['topic']} 的最新市场数据、技术突破和竞争格局..."
    return {"content": [search_data]}

# --- 节点 C: Reviewer (审核与撰稿) ---
def reviewer_node(state: ResearchState):
    if state.get("review_feedback"):
        # 如果有反馈，说明是重写
        prompt = f"根据之前的反馈 '{state['review_feedback']}'，请重新完善这份关于 {state['topic']} 的深度研报。"
    else:
        prompt = f"请根据以下素材写一份专业的研报：\n{''.join(state['content'])}"
    
    res = llm.invoke([SystemMessage(content=prompt)])
    
    # 模拟审核逻辑：如果字数太少，就认为不合格
    if len(res.content) < 200:
        return {"review_feedback": "内容太单薄，请增加行业背景和案例分析。"}
    return {"report": res.content, "review_feedback": "合格"}

# --- 路由逻辑：判断是“打回重做”还是“完结” ---
def route_after_review(state: ResearchState):
    if state["review_feedback"] == "合格" or state["steps"] >= 3:
        return "end"
    return "researcher" # 没通过就回研究员节点补充内容

# 3. 构建 LangGraph 状态机
workflow = StateGraph(ResearchState)

workflow.add_node("planner", planner_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("reviewer", reviewer_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "reviewer")

workflow.add_conditional_edges(
    "reviewer",
    route_after_review,
    {
        "end": END,
        "researcher": "researcher"
    }
)

app = workflow.compile()