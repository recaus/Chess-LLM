from fastapi import APIRouter
from schemas.chess_schemas import LLMChatRequest
from services.chess_llm import Chess_LLMService
from typing import List, Dict
import logging, json, re

router = APIRouter(tags=["Chess"])
logger = logging.getLogger(__name__)
llm_service = Chess_LLMService()

def build_prompt(fen: str, history: List[Dict[str, str]]) -> str:
    prompt = f"You are a helpful chess assistant. Current board position (FEN): {fen}\n\n"
    prompt += "The conversation so far:\n"
    for turn in history:
        role = "User" if turn["role"] == "user" else "Assistant"
        prompt += f"{role}: {turn['content']}\n"
    prompt += "\nAnswer the user's latest question clearly and helpfully about the chess game."
    return prompt

@router.post("/api/llm-chat")
async def llm_chat(data: LLMChatRequest):
    prompt = build_prompt(data.fen, data.history)

    try:
        response_text = llm_service.generate(prompt, max_tokens=512)

        logger.debug("=== RAW LLM RESPONSE ===")
        logger.debug(response_text)

        match = re.search(r"```json\s*([\s\S]+?)\s*```", response_text)
        if match:
            json_str = match.group(1).strip()
            try:
                parsed = json.loads(json_str)
                if isinstance(parsed, dict):
                    return {"response": parsed.get("response") or parsed.get("answer") or str(parsed)}
                else:
                    return {"response": str(parsed)}
            except json.JSONDecodeError:
                return {"response": response_text.strip()}
        
        return {"response": response_text.strip()}

    except Exception as e:
        logger.error(f"LLMChat Error: {e}")
        return {"response": f"❌ Error: {str(e)}"}
