import json
import subprocess
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/interactions?key={API_KEY}"


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
            result = globals()[functionName](keyword)
            input = [{
                "type": "function_result",
                "name": functionName,
                "call_id": steps[-1].get("id"),
                "result": [{"type": "text", "text": str(result)}]
            }]
            payload = createPayload(input, response.get("id"))
            response = sendLLMRequest(payload)
        else:
            print(steps[-1].get("content")[-1].get("text"))
            return

    print("Max iterations reached without a final answer.")
def createPayload(input,previousInteractionId):
	payload = {
	"model": "models/gemini-3.5-flash-lite",
	"input": input,
	"system_instruction":"You are a legacy or new codebase archaelogist",
    "generation_config": {
        "max_output_tokens": 1024,
        "thinking_level": "low",
		"temperature":1.0
    },
	"response_format": {
        "type": "text",
        "mime_type": "application/json",
        "schema": {
          "type": "object",
          "properties": {
            "claim": {
              "type": "string",
              "description": """the actual assertion being made, e.g. "Method X is called from three locations in the OrderService class". This is the archaeologist's conclusion."""
            },
            "evidence": {
                "type": "array",
				"items":{
					"type":"object",
					"properties":{
						"file":{"type":"string","description":"path to the source file where evidence was found"},
						"line":{"type":"number","description":"the line number in that file where the relevant code lives"}
					}
				}
            },
			"confidence":{
				"type":"number",
				"description":"how certain the model is in the claim, e.g. 0.85. This becomes important later when you build the Critic/guardrail — low-confidence or evidence-less claims get flagged or rejected.",
			}
		  }
        }
      },
	  "tools": [{
      "type": "function",
      "name": "get_keyword_result",
      "description": "Get the exact file name , line number and snipper for a given keyword in the codebase",
      "parameters": {
        "type": "object",
		"properties":{
			"keyword":{"type":"string","description":"keyword to search in codebase"}
		},
        "required": ["keyword"]
      }
    }]
}
	if(previousInteractionId):
		payload["previous_interaction_id"] = previousInteractionId

	return payload

def sendLLMRequest(payload):
	response = requests.post(URL, json=payload)
	return response.json()

def get_keyword_result(keyword):
	result = subprocess.run(
		["rg",keyword, "./fixture-repo/", "--json"],
		capture_output=True,
		text=True
	)

	matches = []

	for line in result.stdout.splitlines():
		obj = json.loads(line)

		if obj["type"] == "match":
			data = obj["data"]

			matches.append({
				"file": data["path"]["text"],
				"line": data["line_number"],
				"snippet": data["lines"]["text"].rstrip()
			})

	print(matches)
	return matches

# searchKeyword("OrderDao")

ReActLoop()