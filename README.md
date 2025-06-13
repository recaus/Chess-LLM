# LLM Chess Reasoning with Standardized Output

## Project Overview

This project explores the idea of using a large language model (LLM) to understand standardized input, tokenize that input, and return a response in a structured JSON format. The JSON output is designed to be logically readable and can be used to update the state of an external application — in this case, an Angular front end.

## Model Exploration

Initially, I used [Ollama](https://ollama.com) to host the model and tested a few different options including `llama3`, `phi4-mini-reasoning`, and `DeepSeek-R1`. This gave me a good foundation for evaluating how different models handle reasoning versus compliance with a strict output format.

- **Llama3** was the most consistent in returning the correct JSON structure. However, its reasoning sometimes led to odd behavior. For example, in one game, it submitted three illegal moves. When asked why, it concluded that I would eventually gain line of sight on its king and decided the game was hopeless, so it started responding with nonsense moves.

- **Phi4-mini-reasoning** and **DeepSeek-R1** performed better in terms of reasoning through the game. They made smarter decisions during play but often deviated from the required output format, which made them harder to integrate into the frontend logic.

## Moving Beyond Ollama

To gain more control over the inference process, I switched to using [Hugging Face Transformers](https://huggingface.co/docs/transformers/index) with PyTorch. I also wanted to remove the dependency on Ollama’s runtime, especially in case I decide to scale the system or deploy it in a Kubernetes cluster.

Some of the early challenges included:

- Installing dependencies and CUDA
- Managing token limits (e.g., `gpt-2` has a strict 1024-token max)

I initially used `gpt-2`, a compact but limited model. Its token limit required prompt optimization, and while I was able to get it working, it lacked reasoning depth. Eventually, it would fall into loops, repeating the same illegal move in chess once the game reached a certain complexity.

## Future Improvements

To move the project toward production or larger-scale experimentation, here’s what I plan next:

- **Dockerize** the Angular front end and the FastAPI back end into separate containers
- **Deploy** the application on a **Kubernetes cluster**
- **Quantize** models to FP8 or FP16 to enable better reasoning models like `DeepSeek-R1` or `phi4-mini-reasoning`

While `gpt-2` served as a good starting point and proof of concept, its limitations become very clear during longer interactions. A more advanced model with better reasoning and consistent output would bring the project to the next level.

---

## Tech Stack

- Angular (Frontend)
- FastAPI (Backend API)
- PyTorch + Hugging Face Transformers
- Docker (next-step)
- Kubernetes (next-step)
- Tested LLMs: `llama3`, `phi4-mini-reasoning`, `DeepSeek-R1`, `gpt-2`

---

## Sample Output (JSON Format)

```json
{
  "llmMove": "e7e5",
  "commentary": "Opening with e5"
}
