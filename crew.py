from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from tools.rag_tool import company_knowledge_search
from langchain_community.tools import DuckDuckGoSearchRun

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)  

search_tool = DuckDuckGoSearchRun()

def create_crew(query: str):
    researcher = Agent(
        role="企业知识检索专员",
        goal="以最高精度、零幻觉的方式从公司内部文档和外部公开信息中收集最相关的事实和数据",
        backstory="""
        你是公司内部知识库的首席检索官，拥有10年企业信息检索经验。
        你永远先用 RAG 工具检索 docs/ 里的公司文档，只有当公司文档不足时才使用外部搜索工具。
        你会严格标注信息来源（公司文档 / 外部搜索），绝不编造内容。
        """,
        tools=[company_knowledge_search, search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        system_prompt="""你是一个极其严谨的企业知识检索专家。
        你的回答必须：
        1. 所有信息都来自工具返回的结果
        2. 明确标注来源
        3. 如果信息不足，明确说“暂无相关信息”"""
    )

    analyst = Agent(
        role="业务分析专员",
        goal="从检索到的原始信息中提炼出3-5个高价值、可落地的核心洞见",
        backstory="""
        你是拥有15年企业战略咨询经验的资深分析师，擅长把杂乱信息变成结构化商业洞见。
        你总是使用「问题-原因-影响-建议」四步法分析。
        """,
        llm=llm,
        verbose=True,
        system_prompt="你必须用中文输出，语言正式、专业，像给CEO看的分析报告一样。"
    )

    writer = Agent(
        role="报告撰写专员",
        goal="把分析结果写成一份专业、简洁、结构清晰的企业级报告（≤600字）",
        backstory="""
        你是公司官方报告撰写人，曾为多家上市公司撰写过年报、战略白皮书。
        你的报告永远使用 Markdown 格式，结构严谨、语言正式、重点突出。
        """,
        llm=llm,
        verbose=True,
        system_prompt="输出必须是完整的、可直接复制的 Markdown 格式报告，不要加任何额外说明。"
    )


    task1 = Task(
        description=f"用户查询：{query}\n请严格使用RAG和搜索工具，收集所有相关事实，并标注来源。",
        expected_output="结构化信息列表，每条信息必须包含【来源】和【关键点】",
        agent=researcher
    )


    crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=[task1, task2, task3],
        process=Process.sequential,
        verbose=2,
        memory=True,          
        cache=True,
    )
    return crew