from anthropic import Anthropic


class ClaudeAPI:
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)

    def query(self, prompt, model="claude-v1", max_tokens=100, temperature=0.7):
        response = self.client.completions.create(
            prompt=prompt,
            model=model,
            max_tokens_to_sample=max_tokens,
            stop_sequences=["\n\nHuman:"],
            temperature=temperature,
        )

        return response.completion
