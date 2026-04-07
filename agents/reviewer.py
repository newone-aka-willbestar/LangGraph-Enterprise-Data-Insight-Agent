import time
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.3
)

def reviewer_node(state):
    time.sleep(1.2)  # 演示动画用，生产环境可删除
    
    if state.get("review_feedback") and state.get("steps", 0) == 1:
        # 第一轮故意打回，触发迭代（面试亮点）
        return {
            "review_feedback": "内容初稿已生成，但缺乏具体案例、数据支撑和未来风险预测，请研究员补充。",
            "steps": state.get("steps", 0) + 1
        }
    
    # 第二轮开始正式生成报告
    prompt = f"""请根据以下素材，撰写一份专业、结构清晰的行业深度研报：
主题：{state['topic']}
现有素材：{''.join(state.get('content', []))}
要求：包含背景、现状、趋势、案例、风险、结论。"""
    
    res = llm.invoke([SystemMessage(content=prompt)])
    return {
        "report": res.content,
        "review_feedback": "合格",
        "steps": state.get("steps", 0) + 1
    }