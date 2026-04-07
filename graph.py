import os
from typing import TypedDict, List, Annotated
import operator
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from agents.planner import planner_node
from agents.researcher import researcher_node
from agents.reviewer import reviewer_node

load_dotenv()

# 1. 定义全局状态（保持不变）
class ResearchState(TypedDict):
    topic: str
    plan: Annotated[List[str], operator.add]
    content: Annotated[List[str], operator.add]
    report: str
    review_feedback: str
    steps: int

# 2. 构建状态机（逻辑更清晰）
workflow = StateGraph(ResearchState)

workflow.add_node("planner", planner_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("reviewer", reviewer_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "reviewer")

# 路由：不合格就回 researcher 补充
def route_after_review(state: ResearchState):
    if state.get("review_feedback") == "合格" or state.get("steps", 0) >= 3:
        return "end"
    return "researcher"

workflow.add_conditional_edges(
    "reviewer",
    route_after_review,
    {"end": END, "researcher": "researcher"}
)

app = workflow.compile()

# 导出供 app.py 使用
__all__ = ["app"]