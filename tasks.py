import os
# 禁用 CrewAI telemetry（防止之前的警告）
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_DISABLE_TRACKING"] = "true"

from crew import create_crew
from celery import Celery

celery_app = Celery(
    "corphelper",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

@celery_app.task
def run_crew_task(query: str):
    try:
        crew = create_crew(query)
        result = crew.kickoff()          # 执行多 Agent 流程
        # 强制转为字符串，彻底避免 Pydantic ValidationError
        return str(result)
    except Exception as e:
        # 捕获所有异常并返回可读信息
        import traceback
        error_detail = traceback.format_exc()
        print("=== CrewAI 执行异常 ===")
        print(error_detail)
        return f"任务执行失败: {str(e)}\n\n详细错误：{error_detail}"