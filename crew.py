import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from tools.rag_tool import company_knowledge_search
from langchain_community.tools import DuckDuckGoSearchRun

# ==================== LLM 配置 ====================
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
)

search_tool = DuckDuckGoSearchRun()

# ==================== Agents ====================
researcher = Agent(
    role="企业知识检索专员",
    goal="精准收集公司内部和外部相关事实",
    backstory="你是公司知识库首席检索官，永远只使用工具返回的内容，严格标注来源。",
    tools=[company_knowledge_search, search_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

analyst = Agent(
    role="业务分析专员",
    goal="提炼高价值商业洞见",
    backstory="你是资深战略分析师，使用结构化方法分析信息。",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

writer = Agent(
    role="报告撰写专员",
    goal="输出专业 Markdown 报告",
    backstory="你是公司官方报告撰写人，输出简洁清晰的 Markdown。",
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# ==================== Tasks ====================
def create_crew(query: str):
    task1 = Task(
        description=f"用户查询：{query}\n请使用工具收集所有相关事实并标注来源。",
        expected_output="结构化信息列表",
        agent=researcher
    )

    task2 = Task(
        description="基于第一步结果，提炼 3-5 个核心洞见。",
        expected_output="商业洞见列表",
        agent=analyst
    )

    task3 = Task(
        description="把前面结果整理成一份专业报告。",
        expected_output="完整的 Markdown 格式报告",
        agent=writer
    )

    crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=[task1, task2, task3],
        process=Process.sequential,
        verbose=True,           
        memory=True,
        cache=True,
    )
    return crew