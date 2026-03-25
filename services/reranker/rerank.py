# services/reranker/rerank.py

from typing import List, Dict


def normalize_scores(results: List[Dict]) -> List[Dict]:
    if not results:
        return results

    scores = [r["score"] for r in results]
    min_s, max_s = min(scores), max(scores)

    if max_s == min_s:
        return results

    for r in results:
        r["score"] = (r["score"] - min_s) / (max_s - min_s)

    return results


def rerank_results(vector_results: List[Dict], keyword_results: List[Dict], top_k: int = 5):

    # normalize both
    vector_results = normalize_scores(vector_results)
    keyword_results = normalize_scores(keyword_results)

    # weighted fusion
    combined = {}

    def add_results(results, weight):
        for r in results:
            key = r["text"]  # simple dedup key

            if key not in combined:
                combined[key] = {
                    "text": r["text"],
                    "score": 0.0
                }

            combined[key]["score"] += r["score"] * weight

    # vector slightly stronger
    add_results(vector_results, weight=0.6)
    add_results(keyword_results, weight=0.4)

    # sort
    ranked = sorted(combined.values(), key=lambda x: x["score"], reverse=True)

    return ranked[:top_k]
