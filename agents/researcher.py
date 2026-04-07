def researcher_node(state):
    # TODO: 这里后续会接入真实 Tool Calling（Tavily / Serper）
    # 当前仍用模拟数据，便于你先跑通
    search_data = f"【模拟搜索结果】关于 {state['topic']} 的最新市场数据、技术突破、政策动态和竞争格局..."
    return {"content": [search_data]}