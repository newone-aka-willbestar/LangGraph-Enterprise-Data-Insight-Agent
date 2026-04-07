from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.3
)

def planner_node(state):
    prompt = f"""你是一个顶级行业分析师。
请将主题 '{state['topic']}' 拆解成 **3 个核心调研方向**，每个方向用一句话描述。
直接返回列表格式，例如：
["方向1", "方向2", "方向3"]"""
    
    res = llm.invoke([SystemMessage(content=prompt)])
    # 简单解析（后续可加强为 JSON 解析）
    plan_list = [line.strip() for line in res.content.split("\n") if line.strip()]
    return {"plan": plan_list[:3], "steps": 1}