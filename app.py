# app.py
import streamlit as st
import time
from graph import app as agent_app

# 1. 页面配置：设置宽屏和专业主题
st.set_page_config(
    page_title="Deep Research Agent Pro", 
    page_icon="🔍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式：让界面看起来更像企业级工具
st.markdown("""
    <style>
    .agent-card {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #e6e9ef;
        background-color: #f8f9fa;
    }
    .reviewer-warning {
        background-color: #fff4e6;
        border-left: 5px solid #fd7e14;
    }
    .report-container {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 侧边栏：展示运行状态
with st.sidebar:
    st.title("🚀 控制面板")
    st.info("当前模式：多智能体协作模式")
    st.write("---")
    st.subheader("📊 运行统计")
    token_usage = st.empty()
    steps_count = st.empty()
    st.write("---")
    if st.button("清空所有记录", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# 3. 主界面
st.title("🔍 行业深度调研智能体")
st.markdown("---")

if "events" not in st.session_state:
    st.session_state.events = []

# 用户输入区域
topic = st.chat_input("输入您想深度调研的主题（例如：2025年中国固态电池产业地图）")

if topic:
    # 初始化
    st.session_state.events = []
    inputs = {"topic": topic, "steps": 0, "content": [], "review_feedback": ""}
    
    # 渲染容器
    log_placeholder = st.container()
    
    with st.status("🛸 Agent 团队正在联合作业...", expanded=True) as status:
        # 实时监听 LangGraph 事件
        for event in agent_app.stream(inputs):
            for node, output in event.items():
                timestamp = time.strftime('%H:%M:%S')
                
                if node == "planner":
                    msg = "📝 **Planner**: 已成功将任务拆解为 3 个关键调研方向。"
                    st.write(f"[{timestamp}] {msg}")
                
                elif node == "researcher":
                    msg = "🌐 **Researcher**: 正在模拟全网检索相关行业数据..."
                    st.write(f"[{timestamp}] {msg}")
                
                elif node == "reviewer":
                    feedback = output.get("review_feedback")
                    if feedback != "合格":
                        msg = f"🧐 **Reviewer**: 审核未通过！反馈意见：{feedback}"
                        st.error(msg) # 这里就是你想要的“警告”动效
                        st.write("🔄 **系统指令**: 正在回溯至研究员节点进行补全...")
                    else:
                        st.success(f"✅ **Reviewer**: 质量评估达标，正在交付最终研报。")
            
            # 这里的 sleep 主要是为了演示动效，实际生产可去掉
            time.sleep(0.8)

        # 获取最终结果
        final_result = agent_app.invoke(inputs)
        status.update(label="✨ 调研任务已圆满完成！", state="complete", expanded=False)

    # 4. 结果展示
    st.markdown("### 📝 深度调研报告全文")
    st.markdown(f'<div class="report-container">', unsafe_allow_html=True)
    st.markdown(final_result["report"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 侧边栏更新
    steps_count.metric("协作轮次", final_result.get("steps", 0))
    token_usage.metric("预计消耗", f"{len(final_result['report']) * 1.5:.0f} Tokens")