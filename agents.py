
from llm import createPayload, sendLLMRequest
from tools import get_keyword_result, get_call_references

scratchpad = []

def ReActLoop(max_iterations=5):
    payload = createPayload("Investigate how order cancellation works in this codebase.", None)
    response = sendLLMRequest(payload)

    for i in range(max_iterations):
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
            print(f"scratchPad : {scratchpad}")
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