# graph.py
import os
import sqlite3
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 1. 定义增强型状态
class AgentState(TypedDict):
    messages: list
    sql_query: str | None
    execution_error: str | None  # 记录 SQL 执行报错
    db_result: str | None       # 记录查询结果
    retry_count: int            # 重试次数，防止死循环

# 2. 初始化模型 (推荐使用 DeepSeek，兼容 OpenAI 格式)
llm = ChatOpenAI(
    model="deepseek-chat", 
    api_key=os.getenv("DEEPSEEK_API_KEY"), 
    base_url="https://api.deepseek.com",
    temperature=0
)

# 数据库 DDL 信息（面试点：Prompt Engineering）
DB_SCHEMA = """
表: orders (订单表)
- order_id: 订单ID
- product_id: 产品ID
- amount: 金额
- order_date: 日期

表: products (产品详情)
- product_id: 产品ID
- product_name: 产品名
- category: 类别
"""

# 节点 A: SQL 生成器
def sql_generator_node(state: AgentState):
    retry_prompt = f"\n上一次执行报错: {state.get('execution_error')}" if state.get('execution_error') else ""
    
    prompt = f"""你是一个 SQL 专家。请根据以下 Schema 编写 SQLite 查询语句来回答用户问题。
    {DB_SCHEMA}
    要求：仅返回 SQL 语句，不要有任何 Markdown 标记。
    {retry_prompt}
    用户问题：{state['messages'][0].content}"""
    
    response = llm.invoke([SystemMessage(content=prompt)])
    return {"sql_query": response.content.strip(), "retry_count": state.get("retry_count", 0) + 1}

# 节点 B: SQL 执行器（带错误捕获）
def sql_executor_node(state: AgentState):
    query = state["sql_query"]
    try:
        conn = sqlite3.connect("enterprise_data.db")
        df = pd.read_sql_query(query, conn)
        conn.close()
        return {"db_result": df.to_string(), "execution_error": None}
    except Exception as e:
        return {"execution_error": str(e), "db_result": None}

# 节点 C: 数据洞察分析器
def insight_node(state: AgentState):
    prompt = f"基于查询结果：{state['db_result']}，请用专业中文总结回答用户问题。"
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": [response]}

# 路由逻辑：判断是否需要重试
def should_retry(state: AgentState) -> Literal["sql_gen", "insight", "end"]:
    if state.get("execution_error") and state.get("retry_count", 0) < 3:
        return "sql_gen"  # 报错了且重试次数不到3次，回去重写
    if state.get("db_result"):
        return "insight"  # 执行成功，去分析
    return "end"

# 构建工作流
workflow = StateGraph(AgentState)
workflow.add_node("sql_gen", sql_generator_node)
workflow.add_node("executor", sql_executor_node)
workflow.add_node("insight", insight_node)

workflow.set_entry_point("sql_gen")
workflow.add_edge("sql_gen", "executor")
workflow.add_conditional_edges("executor", should_retry, {
    "sql_gen": "sql_gen", 
    "insight": "insight",
    "end": END
})
workflow.add_edge("insight", END)

app = workflow.compile()