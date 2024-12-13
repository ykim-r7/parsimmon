import os

from parsimmon.claude_api import ClaudeAPI


def main():
    CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
    claude = ClaudeAPI(CLAUDE_API_KEY)
    prompt = input("Enter prompt > ")
    response = claude.query(prompt)
    print(f"Claude says: \n{response}")


if __name__ == "__main__":
    main()
