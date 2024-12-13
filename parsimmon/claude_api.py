from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import WebBaseLoader
import re

SYSTEM_PROMPT = """You are an expert for answering questions using software documentation.
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. 
Context:"""


def normalize_whitespace_regex(text: str) -> str:
    """
    Normalize whitespace using regex substitution.
    Handles all Unicode whitespace characters.
    """
    return re.sub(r"\s+", " ", text).strip()


class ClaudeAPI:
    client: ChatAnthropic
    context: str

    def __init__(self):
        self.client = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            temperature=0,
            max_tokens=1024,
            timeout=None,
            max_retries=2,
        )
        self.context = ""

    async def load_context(self, urls):
        loader = WebBaseLoader(web_paths=urls)
        async for doc in loader.alazy_load():
            self.context += normalize_whitespace_regex(doc.page_content)

    def query(self, prompt):
        messages = [
            ("system", SYSTEM_PROMPT + self.context),
            ("human", prompt),
        ]
        response = self.client.invoke(messages)

        return response.content
