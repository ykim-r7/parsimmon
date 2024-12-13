import asyncio

from claude_api import ClaudeAPI


async def main():
    claude = ClaudeAPI()
    with open("urls.txt", "r") as f:
        url_list = [url.strip() for url in f.readlines()]

    await claude.load_context(url_list)
    print(claude.context)

    prompt = input("Ask me about sqlalchemy! > ")
    response = claude.query(prompt=prompt)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
