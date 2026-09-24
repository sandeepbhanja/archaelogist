
import json
from queue import PriorityQueue
import numpy as np
from numpy.linalg import norm
from llm import createInvestigationPayload, createPayload, sendEmbeddingRequest, sendLLMRequest
from tools import get_keyword_result, get_call_references

scratchpad = []
flatVectorStore = []

def ReActLoop(query: str,max_iterations=10):
    sub_questions = plan_investigation(query)
    final_query = f"""Goal:{query}, Sub-questions to investigate":{sub_questions}"""
    payload = createPayload(final_query, None)
    response = sendLLMRequest(payload)
    retrieve_related(query)
    for i in range(max_iterations):
        print(f"working response = {response}")
        steps = response.get("steps")
        if not steps:
            print("NO LLM RESPONSE")
            return
        if steps[-1].get("type") == "function_call":
            functionName = steps[-1].get("name")
            keyword = steps[-1].get("arguments").get("keyword")
            if functionName == "get_keyword_result":
                result = get_keyword_result(keyword)

            elif functionName == "get_call_references":
                result = get_call_references(keyword)

            input = []
            scratchpad.append({
				"iteration": i,
				"role": "action",
				"tool": functionName,
				"args": steps[-1].get("arguments"),
			})
            scratchpad.append({
				"iteration": i,
				"role": "observation",
				"tool": functionName,
				"result": [{"type": "text", "text": str(result)}],
			})
			
            input.append({
                "type": "function_result",
                "name": functionName,
                "call_id": steps[-1].get("id"),
                "result": [{"type": "text", "text": str(result)}]
            })
            payload = createPayload(input, response.get("id"))
            response = sendLLMRequest(payload)
        else:
            print(steps[-1].get("content")[-1].get("text"))
            claim = json.loads(steps[-1].get("content")[-1].get("text")).get("claim")
            evidence = json.loads(steps[-1].get("content")[-1].get("text")).get("evidence")
            confidence = json.loads(steps[-1].get("content")[-1].get("text")).get("confidence")
            embedding = sendEmbeddingRequest(claim)
            appendVectorStore(embedding,claim,evidence,confidence,query)
            return

    print("Max iterations reached without a final answer.")

def format_scratchpad(scratchpad):
    lines = []
    for entry in scratchpad:
        if entry["role"] == "action":
            lines.append(f'Iteration {entry["iteration"]} — Action: called {entry["tool"]}({entry["args"]})')
        elif entry["role"] == "observation":
            lines.append(f'Iteration {entry["iteration"]} — Observation: {entry["result"]}')
    return "\n".join(lines)

def appendVectorStore(embedding,claim,evidence,confidence,orignal_query):
    flatVectorStore.append({
        "text":claim,
        "embedding":embedding,
        "metadata":{
            "goal": orignal_query,
            "evidence":evidence,
            "confidence":confidence
        }
    })

def cosineSimilarity(vec1,vec2):
    a = np.array(vec1)
    b = np.array(vec2)
    similarity = np.dot(a, b) / (norm(a) * norm(b))
    return similarity

def retrieve_related(query_text, top_k=3):
    pq = PriorityQueue()
    embedding = sendEmbeddingRequest(query_text)
    for i in flatVectorStore:
        vectorStoreEmbedding = i.get('embedding')
        similarity = cosineSimilarity(embedding,vectorStoreEmbedding)
        pq.put((-1 * similarity, i.get('text')))
    top_k_similarity = []
    i = 0
    while not pq.empty() and i<top_k:
        similarity, text = pq.get()
        top_k_similarity.append({"similarity":-1*similarity,"text":text})
        i = i+1
    print(f"top_k_similarity = {top_k_similarity}")

def plan_investigation(goal:str):
    investigationPayload = createInvestigationPayload(goal)
    response = sendLLMRequest(investigationPayload)
    print(response)
    steps = response.get("steps")
    sub_questions = []
    if(steps):
        print("Plan Investigation = "+steps[-1].get("content")[-1].get("text"))
        sub_questions = json.loads(steps[-1].get("content")[-1].get("text")).get("sub_questions")

    return sub_questions
     