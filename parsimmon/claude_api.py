import uuid
from tempfile import TemporaryDirectory

from ast_grep_py import SgRoot
from langchain_anthropic import ChatAnthropic
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent


@tool
def run_pattern_on(pattern: str, contents: str) -> str:
    """
    stfu
    """
    root = SgRoot(contents, "python")
    node = root.root()
    found = node.find(pattern=pattern)
    if found:
        return found.text()

    return ""


@tool
def run_sg_rule_on(rule: str, contents: str) -> str:
    """
    Runs ast-grep CLI with a rule file on given contents.
    Args:
        rule_file: Path to .yml rule file
        contents: String content to analyze
    Returns:
        Output from sg command
    """
    import subprocess
    import tempfile

    # Write contents to temp file for sg to read
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py") as tmp:
        tmp.write(contents)
        tmp.flush()

        # Run sg with rule file on temp file
        result = subprocess.run(
            ["sg", "scan", "--inline-rule", rule, tmp.name],
            capture_output=True,
            text=True,
        )

        return result.stdout


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
        toolkit = FileManagementToolkit(selected_tools=["write_file"])

        self.tools = [self.search, run_pattern_on, run_sg_rule_on, *toolkit.get_tools()]
        memory = MemorySaver()
        self.agent_executor = create_react_agent(
            self.model, self.tools, checkpointer=memory
        )
        self.config = {"configurable": {"thread_id": str(uuid.uuid4())[:8]}}

    def load_context(self, context):
        self.context += context
        self.context += "\n"

    def query(self, messages):
        messages = {"messages": messages}
        for chunk in self.agent_executor.stream(messages, config=self.config):
            yield (chunk)
