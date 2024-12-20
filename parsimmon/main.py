import argparse
from pathlib import Path

from claude_api import ClaudeAPI
from langchain_core.prompts import ChatPromptTemplate

ast_grep_system_template = """
    Return a valid ast-grep rule file that implements the pattern described in the <Description>.
    Go step-by-step, but ask for user confirmation after each step. 
    First, create a pattern and ensure the syntax is valid by running it against the provided <Example>.
    Second, create a rule containing the pattern and ensure it is valid by running it against the provided <Example>.
    Third, write the rule file to a sensibly-named output file confirmed by the user.
    """

ast_grep_human_template = """
    <Description>
    {description}
    </Description>

    <Example>
    {example}   
    </Example>
"""


def load_schema_context(claude):
    claude.load_context("The following is the schema for an ast-grep rule file: ")
    with open("rule.json", "r") as f:
        claude.load_context(f.read())


def run_cli(args):
    claude = ClaudeAPI()
    first_time = True

    context = ""
    if path_to_context := args.path_to_context:
        with open(path_to_context) as f:
            context = f.read()

    if args.ast_grep_mode:
        print("AST GREP MODE ACTIVATED\n")
        while True:
            messages = []
            if first_time:
                messages = [
                    ("system", ast_grep_system_template),
                    ("human", ast_grep_human_template),
                ]

                user_input = input("\nDescribe your ast-grep rule. > ").strip()

                query_messages = (
                    ChatPromptTemplate(messages)
                    .invoke({"description": user_input, "example": context})
                    .to_messages()
                )

            else:
                user_input = input("\n> ").strip()
                query_messages = [("human", user_input)]

            response = claude.query(query_messages)
            for chunk in response:
                print(chunk)
            first_time = False

    else:
        print("INTERACTIVE MODE ACTIVATED\n")
        while True:
            prompt = input("\nQuery > ").strip()
            response = claude.query(prompt)
            for chunk in response:
                print(chunk)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--ast-grep-mode", action="store_true")
    parser.add_argument("-c", "--path-to-context", type=Path)
    args = parser.parse_args()

    if args.ast_grep_mode and not args.path_to_context:
        parser.error("--path-to-context is required when using --ast-grep-mode")

    run_cli(args)


if __name__ == "__main__":
    main()
