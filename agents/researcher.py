# agents/researcher.py
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
import os

# 初始化 Tavily 搜索工具（返回 5 条高质量结果）
tavily_tool = TavilySearchResults(
    max_results=5,
    search_depth="advanced",      # 可选：advanced 质量更高
    include_answer=True
)

# DeepSeek LLM（保持和 planner/reviewer 一致）
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.3
)

def researcher_node(state):
    """真实联网搜索 + 总结"""
    topic = state["topic"]
    plan = state.get("plan", ["通用调研"])  # 如果 planner 还没拆分，就用默认

    # 1. 调用 Tavily 搜索（支持中文）
    search_query = f"{topic} {plan[0] if plan else ''} 最新市场 数据 趋势 案例"
    search_results = tavily_tool.invoke(search_query)

    # 2. 用 LLM 把搜索结果总结成结构化素材（提升报告质量）
    prompt = f"""请将以下搜索结果整理成清晰的调研素材，每条素材控制在 2-3 句话：
    搜索主题：{topic}
    搜索结果：{search_results}
    要求：提取关键数据、趋势、公司/案例、政策等。"""

    summary = llm.invoke([SystemMessage(content=prompt)]).content

    return {
        "content": [f"【第 {state.get('steps', 1)} 轮搜索结果】\n{summary}"],
        "steps": state.get("steps", 0) + 1
    }