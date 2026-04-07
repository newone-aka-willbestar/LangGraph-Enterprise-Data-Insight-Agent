# app.py （纯 Streamlit 前端）
import streamlit as st
import requests
import time

st.set_page_config(page_title="LangGraph 企业级数据洞察 Agent", layout="wide")
st.title(" LangGraph 生产级 ReAct 多智能体数据洞察 Agent")
st.caption("FastAPI 后端 + 高并发 | DeepSeek + Tavily 真实搜索")

# 输入
topic = st.text_input("请输入调研主题（支持中文）", 
                      placeholder="2025 中国固态电池产业地图",
                      value="2025 中国固态电池产业地图")

if st.button("🚀 开始多智能体分析", type="primary", use_container_width=True):
    if not topic:
        st.error("请输入主题！")
        st.stop()

    with st.spinner("正在调用后端 Agent（Planner → Researcher → Reviewer 迭代中...）"):
        try:
            # 调用 FastAPI
            response = requests.post(
                "http://127.0.0.1:8000/research",
                json={"topic": topic},
                timeout=180
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 展示结果
                st.success("✅ 分析完成！")
                st.subheader("📋 调研计划")
                for i, p in enumerate(data["plan"], 1):
                    st.write(f"{i}. {p}")
                
                st.subheader("📊 最终研报")
                st.markdown(data["report"])
                
                st.caption(f"共 {data['steps']} 步迭代 | 最后两轮搜索摘要已显示")
                for snippet in data.get("content_snippets", []):
                    with st.expander("搜索素材摘要"):
                        st.write(snippet)
            else:
                st.error(f"后端错误: {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ 无法连接到后端！请先启动 FastAPI 服务（见下方）")
        except Exception as e:
            st.error(f"请求失败: {str(e)}")
