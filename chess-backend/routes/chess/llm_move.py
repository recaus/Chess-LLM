import random
from fastapi import APIRouter
from schemas.chess_schemas import ChessMoveRequest
from services.chess_llm import Chess_LLMService
from config import CHESS_LLM_PROMPT, CHESS_LLM_PROMPT_FOOTER
import chess, json, logging, re

router = APIRouter(tags=["Chess"])
logger = logging.getLogger(__name__)
llm_service = Chess_LLMService()
ENABLE_LLM_MOVE_FALLBACK = True

@router.post("/api/llm-move")
async def llm_move(data: ChessMoveRequest):
    logger.debug(f"\n=== LLM-MOVE CALLED ===")
    logger.debug(f"Received FEN: {data.fen}")
    logger.debug(f"Player Move: {data.playerMove}")

    try:
        board = chess.Board(data.fen)
    except ValueError as e:
        logger.error(f"Invalid FEN: {e}")
        return {"llmMove": "none", "commentary": "Invalid FEN format."}

    try:
        move = chess.Move.from_uci(data.playerMove)
    except ValueError:
        logger.error("Invalid player move format")
        return {"llmMove": "none", "commentary": "Invalid move format."}

    if move not in board.legal_moves:
        logger.error("Player move is illegal")
        return {"llmMove": "none", "commentary": "Illegal move."}

    player_move_san = board.san(move)
    board.push(move)
    new_fen = board.fen()
    logger.debug(f"FEN after player move: {new_fen}")

    ai_legal_moves = [
        {"from_square": m.from_square, "to": m.to_square, "san": board.san(m), "promotion": m.promotion}
        for m in board.legal_moves
    ]

    def query_llm(illegal_moves: list[str]):
        uci_moves = [board.uci(m) for m in board.legal_moves]
        base_prompt = (
            CHESS_LLM_PROMPT +
            f"Human ({data.humanPieceColor}) just played: {player_move_san} ({data.playerMove})\n"
            f"FEN: {board.fen()}\n"
            f"Your turn as {data.aiPieceColor}. Legal UCI moves: {', '.join(uci_moves)}\n"
            "Format:\n"
            "```json\n"
            "{\"llmMove\": \"e7e5\", \"commentary\": \"Opening with e5\"}\n"
            "```\n"
        )
        if illegal_moves:
            base_prompt += f"WARNING: Previous illegal moves: {', '.join(illegal_moves)}\n"
        base_prompt += CHESS_LLM_PROMPT_FOOTER

        try:
            response_text = llm_service.generate(base_prompt, max_tokens=256)
            logger.debug(f"=== RAW LLM RESPONSE ===\n{response_text}\n========================")

            match = re.search(r"```json\s*([\s\S]+?)\s*```", response_text, re.DOTALL)
            if match:
                json_string = match.group(1).strip()
                logger.debug(f"Extracted JSON: {json_string}")
                parsed = json.loads(json_string)
                if isinstance(parsed, dict) and "llmMove" in parsed:
                    return parsed.get("llmMove", "none"), parsed.get("commentary", "")
                return None, "Parsed JSON is not a dict with llmMove"

            cleaned_raw = response_text.strip('` \n\r\t')
            parsed = json.loads(cleaned_raw)
            if isinstance(parsed, dict) and "llmMove" in parsed:
                return parsed.get("llmMove", "none"), parsed.get("commentary", "")
            return None, "Raw JSON is not a dict with llmMove"
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return None, f"Invalid JSON format: {e}"
        except Exception as e:
            logger.error(f"Unexpected error in query_llm: {e}")
            return None, f"Unexpected error: {e}"

    MAX_RETRIES = 3
    retries = 0
    illegal_moves = []

    while retries < MAX_RETRIES:
        llm_move, commentary = query_llm(illegal_moves)
        if llm_move is None:
            logger.error(f"LLM query failed: {commentary}")
            return {"llmMove": "none", "commentary": commentary}

        logger.debug(f"LLM Move Returned: {llm_move}")
        logger.debug(f"Commentary: {commentary}")

        if llm_move == "none":
            return {"llmMove": "none", "commentary": commentary}

        try:
            move_obj = chess.Move.from_uci(llm_move)
        except ValueError:
            try:
                move_obj = board.parse_san(llm_move)
                llm_move = move_obj.uci()
                logger.debug(f"Converted SAN move to UCI: {llm_move}")
            except ValueError:
                illegal_moves.append(llm_move)
                logger.error(f"Invalid move format (neither UCI nor SAN): {llm_move}")
                retries += 1
                continue

        if move_obj not in board.legal_moves:
            if ENABLE_LLM_MOVE_FALLBACK:
                logger.warning(f"Illegal move returned by LLM: {llm_move}")
                
                # Fallback: pick a random legal move instead
                legal_uci_moves = [move.uci() for move in board.legal_moves]
                fallback_move = random.choice(legal_uci_moves)
                logger.warning(f"Using fallback legal move: {fallback_move}")
                
                fallback_obj = chess.Move.from_uci(fallback_move)
                board.push(fallback_obj)
                return {"llmMove": fallback_move, "commentary": f"LLM move '{llm_move}' was illegal. Fallback move selected."}
            else:
                illegal_moves.append(llm_move)
                retries += 1
                continue


        board.push(move_obj)
        logger.debug("LLM move applied successfully")
        return {"llmMove": llm_move, "commentary": commentary}

    logger.error(f"Failed to get legal move after {MAX_RETRIES} attempts. Illegal moves: {illegal_moves}")
    return {
        "llmMove": "none",
        "commentary": f"Failed after {MAX_RETRIES} attempts. Illegal moves: {', '.join(illegal_moves)}"
    }