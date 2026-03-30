# CorpHelper - 企业级分布式多Agent助手

**学生打造的企业级 AI Agent 实战项目**  
支持 **RAG + 多Agent协作 + Celery 分布式任务队列 + Docker 一键部署**，完美复刻公司内部知识助手生产架构。

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) 
![Docker](https://img.shields.io/badge/Docker-Ready-green)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-orange)

## ✨ 核心特性
- **企业级 RAG**：自动读取 `docs/` 文件夹里的 PDF/TXT/MD，作为公司知识库
- **多Agent协作**：Researcher → Analyst → Writer 三角色流水线（CrewAI）
- **分布式任务**：Celery + Redis 支持水平扩容（`--scale worker=10`）
- **混合检索**：公司内部文档 + DuckDuckGo 外部搜索
- **异步前端**：Streamlit + FastAPI + 实时轮询结果
- **一键部署**：`docker compose up` 即可本地或服务器运行

## 🚀 快速启动（3 分钟跑通）

1. 克隆项目
   ```bash
   git clone https://github.com/newone-aka-willbestar/corphelper.git
   cd corphelper

## 🏗️ 架构图
Streamlit UI (前端)
    ↓ HTTP POST
FastAPI Gateway (api.py)
    ↓ Celery Task Queue (Redis Broker)
Celery Worker × N（可分布式部署）
    ↓
CrewAI 多Agent 流水线
    ├── Researcher → RAG Tool (Chroma) + DuckDuckGo
    ├── Analyst     → 结构化洞见提取
    └── Writer      → Markdown 专业报告
    ↓
Redis Backend 存储结果 → Streamlit 实时展示


## 🛠️ 技术栈
前端：Streamlit
后端：FastAPI
Agent 框架：CrewAI + LangChain
向量数据库：Chroma（可轻松替换为 PGVector）
任务队列：Celery + Redis
搜索工具：DuckDuckGo
部署：Docker + docker-compose

## 📋 未来规划（Roadmap）
 支持 LangGraph（状态机 + human-in-the-loop）（）
 Prompt 工程模板化（prompts.yaml 可配置）（）
 多 LLM 支持（LiteLLM + 通义千问/DeepSeek）（）
 生产级向量库（PGVector / Qdrant）（）
 监控 + 日志（LangSmith + Prometheus）（）
 JWT 鉴权 + 多租户（）
 CI/CD + 单元测试（）

欢迎 Star ⭐ 并提交 Issue / PR！
这个项目会持续迭代，成为应届生最好的企业级 AI Agent 学习模板。


