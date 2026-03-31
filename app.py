import streamlit as st
from graph import app as graph_app
from langchain_core.messages import HumanMessage

st.title("🚀 LangGraph DataInsight Agent")
st.caption("智能大数据分析 Agent · 支持高并发 + 大数据处理")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("请输入你的数据分析需求（例如：分析 sales.parquet 文件）"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("Agent 正在思考并调用工具..."):
        initial_state = {
            "messages": [HumanMessage(content=prompt)],
            "dataset_path": "data/sales.parquet",
            "insights": []
        }
        result = graph_app.invoke(initial_state)
        
        final_msg = result["messages"][-1].content
        st.session_state.messages.append({"role": "assistant", "content": final_msg})
        st.chat_message("assistant").write(final_msg)
        
        if "insights" in result and result["insights"]:
            st.subheader("📊 生成的洞察")
            for insight in result["insights"]:
                st.success(insight)