# services/retriever/keyword_search.py


async def keyword_search(query: str):
    return [{"text": f"keyword result for {query}", "score": 0.7}]
