# app.py
import streamlit as st
from graph import app as agent_app

st.set_page_config(page_title="AI 行业深度调研助手", layout="wide")
st.title("🔍 AI 行业深度调研 Agent")
st.caption("多智能体协作：Planner -> Researcher -> Reviewer (闭环修正)")

if topic := st.chat_input("输入调研主题（例如：2024中国人形机器人产业趋势）"):
    st.chat_message("user").write(topic)
    
    with st.status("Agent 正在多体协作中...", expanded=True) as status:
        # 初始化
        inputs = {"topic": topic, "steps": 0, "content": [], "review_feedback": ""}
        
        for event in agent_app.stream(inputs):
            for node, output in event.items():
                if node == "planner":
                    st.write("📝 **Planner**: 正在拆解调研大纲...")
                elif node == "researcher":
                    st.write("🌐 **Researcher**: 正在全网检索实时资料...")
                elif node == "reviewer":
                    if output.get("review_feedback") != "合格":
                        st.warning(f"🧐 **Reviewer**: 发现内容不足，已打回重做...")
                    else:
                        st.success("✅ **Reviewer**: 审核通过，正在排版报告...")
        
        result = agent_app.invoke(inputs)
        status.update(label="调研完成！", state="complete")

    st.markdown("### 📝 深度调研报告")
    st.markdown(result["report"])