from fastapi import FastAPI
from pydantic import BaseModel
from tasks import run_crew_task
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult   # ← 必须加上这一行

app = FastAPI(title="CorpHelper 企业分布式AI助手")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/generate")
async def generate_report(request: QueryRequest):
    task = run_crew_task.delay(request.query)
    return {
        "task_id": task.id,
        "message": "任务已提交到分布式队列，Worker正在处理..."
    }

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    task = AsyncResult(task_id)          # ← 使用正确的 AsyncResult
    
    if task.ready():
        if task.failed():
            return {
                "status": "FAILURE",
                "error": str(task.result) if task.result else "未知错误"
            }
        else:
            return {
                "status": "SUCCESS",
                "result": task.result
            }
    else:
        return {"status": "PENDING"}