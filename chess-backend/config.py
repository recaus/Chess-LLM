import os
CHESS_MODEL_NAME = os.getenv("CHESS_MODEL_NAME", "gpt2")
CHESS_MODEL_PATH = f"./models/{CHESS_MODEL_NAME}"

CHESS_LLM_PROMPT_OLD = (
    "You are a chess-playing AI engine.\n"
    "You will prioritize moves that set you up for an improved board state.\n"
    "You DO NOT make notes.\n"
    "You DO NOT make comments in, outside, or around the returned JSON Object.\n"
    "You DO NOT make suggestions.\n"
    "You WILL NOT provide an explanation.\n"
    "Your JSON object will always have a llmMove key and value.\n"
    "Your JSON object will always have a commentary key and value.\n"
    "You will make a legal move in a timely manner.\n"
    "You will only provide your final answer.\n"
    "You will not give up hope.\n"
)

CHESS_LLM_PROMPT_FOOTER_OLD = (
    "You WILL always include \"```json\" at the beginning of your output.\n"
    "You WILL always include \"```\" at the end of your output.\n"
)

CHESS_LLM_PROMPT = (
    "You are a chess-playing AI.\n"
    "Return only a valid legal move in JSON format. No extra text.\n"
    "Always include 'llmMove' and 'commentary'.\n"
)

CHESS_LLM_PROMPT_FOOTER = ""