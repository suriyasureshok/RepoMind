# pipeline/query_pipeline.py

import asyncio

from services.llm.client import LLMClient
from services.reranker import rerank_results
from services.retriever import keyword_search, vector_search


async def run_query_pipeline(query: str):

    # 1. preprocess
    clean_query = query.strip().lower()

    # 2. parallel retrieval
    vector_results, keyword_results = await gather_results(clean_query)

    # 3. rerank
    top_chunks = rerank_results(vector_results, keyword_results)

    # 4. context build
    context = build_context(top_chunks)

    # 5. LLM call
    llm = LLMClient()
    response = await llm.generate(context, clean_query)

    return response


async def gather_results(query: str):
    vector_task = vector_search(query)
    keyword_task = keyword_search(query)

    return await asyncio.gather(vector_task, keyword_task)


def build_context(chunks):
    context = "\n\n".join([c["text"] for c in chunks])

    return context[:3000]
