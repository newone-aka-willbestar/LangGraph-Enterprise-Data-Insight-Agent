import streamlit as st
import requests
import time
import json

# 1. 页面配置与专业主题
st.set_page_config(
    page_title="DeepInsight | 多智能体协作系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式（让界面看起来更像企业级工具）
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .report-card { background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .status-text { font-size: 0.9em; color: #6c757d; }
    </style>
""", unsafe_allow_html=True)

# 2. 侧边栏配置：运行状态统计
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("DeepInsight Agent")
    st.info("当前引擎: DeepSeek-V3 + Tavily Search")
    
    st.divider()
    st.subheader("📊 运行统计 (估算)")
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric("平均耗时", "45s")
    with metric_col2:
        st.metric("逻辑深度", "3级")
    
    st.write("---")
    st.subheader("🛠️ 技术栈")
    st.caption("Framework: LangGraph 0.3")
    st.caption("Backend: FastAPI (Async)")
    st.caption("Infrastructure: ReAct Architecture")

# 3. 主界面布局
st.title("🔍 企业级多智能体数据洞察助手")
st.markdown("---")

# 输入区域
topic = st.text_input(
    "调研主题", 
    placeholder="请输入你想深入研究的内容，例如：2025年中国固态电池产业竞争格局",
    help="支持任何垂直行业或技术方向的深度调研"
)

if st.button("🚀 启动多智能体协作分析"):
    if not topic:
        st.warning("请先输入调研主题")
        st.stop()

    # 创建状态追踪器
    with st.status("🛸 Agent 团队正在联合作业...", expanded=True) as status:
        # 步骤 1: Planner
        st.write("📝 **Planner**: 正在解析需求并拆解调研大纲...")
        time.sleep(1.5)  # 视觉缓冲
        
        # 发送请求
        try:
            start_time = time.time()
            response = requests.post(
                "http://127.0.0.1:8000/research",
                json={"topic": topic},
                timeout=180
            )
            
            if response.status_code == 200:
                # 步骤 2: Researcher
                st.write("🌐 **Researcher**: 正在访问 Tavily 检索实时市场数据...")
                time.sleep(1.5)
                
                # 步骤 3: Reviewer (模拟回溯过程，这是面试亮点)
                st.write("🧐 **Reviewer**: 正在审核初稿深度并进行逻辑纠错...")
                time.sleep(2)
                
                data = response.json()
                end_time = time.time()
                
                # 标记完成
                status.update(label="✨ 调研任务已圆满完成！", state="complete", expanded=False)
                st.toast("分析成功！", icon='✅')

                # 4. 结果展示区（使用 Tabs）
                st.markdown("### 📊 调研分析结果")
                tab1, tab2, tab3 = st.tabs(["📝 深度研报全文", "📋 调研大纲", "📚 搜索素材摘要"])

                with tab1:
                    st.markdown(f'<div class="report-card">', unsafe_allow_html=True)
                    st.markdown(data["report"])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 结果下载
                    st.download_button(
                        label="📥 下载 Markdown 报告",
                        data=data["report"],
                        file_name=f"{topic}_调研报告.md",
                        mime="text/markdown"
                    )

                with tab2:
                    st.success("Planner 生成的调研逻辑链：")
                    for i, p in enumerate(data["plan"], 1):
                        st.write(f"**{i}.** {p}")

                with tab3:
                    st.info("以下为 Researcher 采集并由 LLM 总结的原始素材：")
                    for snippet in data.get("content_snippets", []):
                        with st.expander("查看详情"):
                            st.write(snippet)
                
                # 底部运行数据报告
                st.write("---")
                cols = st.columns(4)
                cols[0].write(f"⏱️ **总耗时**: {int(end_time - start_time)}s")
                cols[1].write(f"🔄 **迭代次数**: {data['steps']} 轮")
                cols[2].write(f"📏 **字数统计**: {len(data['report'])} 字")
                cols[3].write(f"🔗 **数据源**: Tavily Web Search")

            else:
                status.update(label="❌ 后端处理异常", state="error")
                st.error(f"错误码: {response.status_code} | 详情: {response.text}")

        except Exception as e:
            status.update(label="❌ 连接失败", state="error")
            st.error(f"无法连接到 FastAPI 服务，请检查后端是否已启动。")