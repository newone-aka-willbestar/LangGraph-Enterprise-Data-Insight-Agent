# app.py
import streamlit as st
from graph import app as graph_app
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="DataInsight Agent v2.0", layout="wide")
st.title("📊 企业多维数据智能助手")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 用户输入
if prompt := st.chat_input("例如：哪个产品的销售额最高？"):
    st.chat_message("user").write(prompt)
    
    with st.status("Agent 正在思考...", expanded=True) as status:
        initial_state = {
            "messages": [HumanMessage(content=prompt)],
            "retry_count": 0
        }
        
        # 运行 Agent 并监听事件
        for event in graph_app.stream(initial_state):
            for node, output in event.items():
                if "sql_query" in output:
                    st.code(f"生成 SQL: {output['sql_query']}", language="sql")
                if "execution_error" in output and output["execution_error"]:
                    st.error(f"❌ 执行出错: {output['execution_error']}")
                if "db_result" in output and output["db_result"]:
                    st.success("✅ 查询成功，获取到数据")
        
        result = graph_app.invoke(initial_state) # 最终拿结果
        final_answer = result["messages"][-1].content
        status.update(label="分析完成！", state="complete")

    st.chat_message("assistant").write(final_answer)