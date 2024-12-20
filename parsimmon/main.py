import argparse
from pathlib import Path

from claude_api import ClaudeAPI
from langchain_core.prompts import ChatPromptTemplate

context_system_template = """

"""

ast_grep_template = """
    Return a valid ast-grep rule file that implements that pattern.
    Go step-by-step.
    First, create a pattern and ensure the syntax is valid by running it against the provided <Example>.
    Second, create a rule file for the pattern and ensure it is valid by running it against the provided <Example>.
    Third, write the rule file to a sensibly-named output file.
    <Description>
    {description}
    </Description>

    <Example>
    {example}
    </Example>
    """

pattern_valid = False


def load_schema_context(claude):
    claude.load_context("The following is the schema for an ast-grep rule file: ")
    with open("rule.json", "r") as f:
        claude.load_context(f.read())


def run_cli(args):
    claude = ClaudeAPI()

    context = ""
    if path_to_context := args.path_to_context:
        with open(path_to_context) as f:
            context = f.read()

    if args.ast_grep_mode:
        print("AST GREP MODE ACTIVATED\n")
        prompt_template = ChatPromptTemplate.from_template(ast_grep_template)

        user_prompt = input("\nDescribe your ast-grep rule > ").strip()
        prompt = prompt_template.invoke(
            {"description": user_prompt, "example": context}
        )
        messages = prompt.to_messages()
        response = claude.query(messages)
        for chunk in response:
            print(chunk)

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
