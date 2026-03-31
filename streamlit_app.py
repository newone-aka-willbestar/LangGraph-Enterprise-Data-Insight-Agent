import streamlit as st
import requests
import time

st.set_page_config(page_title="CorpHelper", page_icon="🏢", layout="wide")
st.title("🏢 CorpHelper - 企业分布式智能助手")

query = st.text_area(
    "请输入你的任务需求：",
    height=120,
    placeholder="例如：生成2026年Q2 AI工具应用趋势报告..."
)

if st.button("🚀 生成报告", type="primary"):
    if not query.strip():
        st.warning("请输入查询内容")
        st.stop()

    with st.spinner("任务已进入分布式队列，多Worker正在协作处理..."):
        # 提交任务
        response = requests.post(
            "http://localhost:8000/generate",
            json={"query": query}
        )
        
        if response.status_code != 200:
            st.error(f"提交任务失败: {response.text}")
            st.stop()

        data = response.json()
        task_id = data["task_id"]
        st.info(f"✅ 任务已提交！**Task ID**: `{task_id}`")

        # 安全轮询（解决 JSONDecodeError）
        placeholder = st.empty()
        for i in range(60):  # 最多等待 2 分钟
            time.sleep(2)
            result_resp = requests.get(f"http://localhost:8000/result/{task_id}")
            
            if result_resp.status_code != 200:
                placeholder.error(f"接口错误 {result_resp.status_code}: {result_resp.text}")
                break

            try:
                result_data = result_resp.json()
            except requests.exceptions.JSONDecodeError:
                raw = result_resp.text.strip()
                placeholder.warning(f"接口返回非 JSON（任务可能还在处理）:\n{raw}")
                continue

            status = result_data.get("status")
            
            if status == "SUCCESS":
                st.success("✅ 报告生成完成！")
                st.markdown("### 生成报告")
                st.markdown(result_data.get("result", "无报告内容"))
                break
            elif status == "FAILURE":
                st.error(f"❌ 任务执行失败\n{result_data.get('error', '未知错误')}")
                break
            else:
                placeholder.info(f"⏳ 任务正在处理中...（已等待 { (i+1)*2 } 秒）状态: **{status}**")
        else:
            st.warning("⏰ 等待超时，请稍后使用 Task ID 查询结果")