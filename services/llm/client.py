# services/llm/client.py

import asyncio


class LLMClient:

    async def generate(self, context: str, query: str):

        # fake LLM for now
        await asyncio.sleep(0.5)

        return f"""
Context:
{context}

Answer:
This is a generated response for query: {query}
"""
