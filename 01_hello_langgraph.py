import os
from dotenv import load_dotenv

# ==================== LangGraph 核心导入 ====================
from langgraph.graph import StateGraph, START, END

# Python 标准库（用来定义 State）
from typing import TypedDict, Annotated
import operator

load_dotenv()

# ==================== 1. 定义全局 State ====================
class AgentState(TypedDict):
    messages: Annotated[list[str], operator.add]   # 自动累加消息
    dataset_path: str | None
    insights: list[str]

# ==================== 2. 定义 Node（现在拆成3个节点！） ====================
def planner_node(state: AgentState) -> AgentState:
    print("📋 Planner: 正在规划任务...")
    return {"messages": ["任务规划完成：分片处理 + 分析 + 生成报告"]}

def data_cleaner_node(state: AgentState) -> AgentState:
    print("🧹 Data Cleaner: 正在清洗数据（去除空值、统一格式）...")
    # 这里以后可以真正调用 pandas/polers 做清洗
    return {"messages": ["数据清洗完成"]}

def insight_generator_node(state: AgentState) -> AgentState:
    print("🔍 Insight Generator: 正在生成分析洞察...")
    # 这里以后会调用 LLM 或统计工具
    return {
        "messages": ["已生成3条洞察"],
        "insights": ["平均值提升15%", "发现异常峰值", "趋势向上"]
    }

# ==================== 3. 构建 Graph（关键修改在这里！） ====================
workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("data_cleaner", data_cleaner_node)      # ← 新增节点
workflow.add_node("insight_generator", insight_generator_node)  # ← 新增节点

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "data_cleaner")              # ← planner 完成后 → data_cleaner
workflow.add_edge("data_cleaner", "insight_generator")    # ← data_cleaner 完成后 → insight_generator
workflow.add_edge("insight_generator", END)               # ← 最后结束

# ==================== 4. 编译 & 运行 ====================
app = workflow.compile()

result = app.invoke({
    "messages": [], 
    "dataset_path": "data/sales.csv", 
    "insights": []
})

print("\n✅ 最终结果：")
print(result)