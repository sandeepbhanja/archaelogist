import json

import requests
import os
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/interactions?key={API_KEY}"
EMBEDDING_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent"


def createPayload(input,previousInteractionId):
	payload = {
	"model": "models/gemini-3.5-flash-lite",
	"input": input,
	"system_instruction":"You are a legacy or new codebase archaelogist. You have a max of 4 iteration to ask stuff and give output",
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
	  "tools": [
    {
        "type": "function",
        "name": "get_keyword_result",
        "description": "Get the exact file name, line number and snippet for a given keyword in the codebase (plain text/substring search — matches any occurrence, including imports, comments, and declarations).",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "keyword to search in codebase"}
            },
            "required": ["keyword"]
        }
    },
    {
        "type": "function",
        "name": "get_call_references",
        "description": "Find every call site of a given method across the codebase using AST-level parsing, not text search. Matches only actual method_invocation nodes — ignores the method's own declaration and any textual matches that aren't real call sites (variable names, comments). Works regardless of whether the containing class is annotated (@Service, @Repository) or a plain unannotated class.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "exact method name to find call sites of"}
            },
            "required": ["keyword"]
        }
    }
]
}
	if(previousInteractionId):
		payload["previous_interaction_id"] = previousInteractionId

	return payload

def sendLLMRequest(payload):
	response = requests.post(URL, json=payload)
	return response.json()

def sendEmbeddingRequest(payload):
	headers = {"x-goog-api-key":API_KEY}
	body = {
		 "model": "models/gemini-embedding-2",
        "content": {
        "parts": [{
            "text": payload
        }]
        }
    }
	response = requests.post(EMBEDDING_URL,headers=headers,json=body)
	return response.json().get("embedding").get("values")