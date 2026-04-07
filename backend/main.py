from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

from graph import app as agent_app  # 复用我们已经优化好的 LangGraph

app = FastAPI(
    title="LangGraph Enterprise Data Insight Agent API",
    description="生产级 ReAct 多智能体数据洞察后端 - 支持高并发",
    version="1.0.0"
)

# 允许 Streamlit 前端跨域调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议改成具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    report: str
    steps: int
    plan: List[str]
    content_snippets: List[str]

# 全局状态缓存（生产建议换成 Redis）
research_cache: Dict[str, ResearchResponse] = {}

@app.post("/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="主题不能为空")

    # 异步执行 LangGraph（支持高并发）
    try:
        # 使用 LangGraph 的 ainvoke 支持异步
        result = await agent_app.ainvoke({
            "topic": topic,
            "plan": [],
            "content": [],
            "report": "",
            "review_feedback": "",
            "steps": 0
        })

        response = ResearchResponse(
            report=result.get("report", "生成失败"),
            steps=result.get("steps", 0),
            plan=result.get("plan", []),
            content_snippets=result.get("content", [])[-2:]  # 只返回最近两次搜索摘要
        )

        # 缓存结果（可选）
        research_cache[topic] = response
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 执行失败: {str(e)}")

# 健康检查
@app.get("/health")
async def health():
    return {"status": "ok", "concurrency_ready": True}

# 启动命令（终端运行）：
# uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4