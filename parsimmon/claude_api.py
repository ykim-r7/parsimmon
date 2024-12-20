from ast_grep_py import SgRoot
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

SYSTEM_PROMPT = """You're a good Claude and you like to use tools!"""


@tool
def run_ast_grep_on(pattern: str, contents: str) -> str:
    """
    stfu
    """
    root = SgRoot(contents, "python")
    node = root.root()
    found = node.find(pattern=pattern)
    if found:
        return found.text()

    return ""


class ClaudeAPI:
    model: ChatAnthropic
    context: str
    search: None
    tools: []
    agent_executor: None

    def __init__(self):
        self.model = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            temperature=0,
            max_tokens=1024,
            timeout=None,
            max_retries=2,
        )
        self.context = ""
        self.search = TavilySearchResults(max_results=2)
        self.tools = [self.search, run_ast_grep_on]
        memory = MemorySaver()
        self.agent_executor = create_react_agent(
            self.model, self.tools, checkpointer=memory
        )
        self.config = {"configurable": {"thread_id": "abc123"}}

    def load_context(self, context):
        self.context += context
        self.context += "\n"

    def query(self, messages):
        messages = {"messages": messages}
        for chunk in self.agent_executor.stream(messages, config=self.config):
            yield (chunk)
