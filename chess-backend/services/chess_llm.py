from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
from config import CHESS_MODEL_PATH



class Chess_LLMService:
    def __init__(self, local_model_path=CHESS_MODEL_PATH):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = GPT2Tokenizer.from_pretrained(local_model_path, local_files_only=True)
        self.model = GPT2LMHeadModel.from_pretrained(local_model_path, local_files_only=True).to(self.device)

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.7) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
