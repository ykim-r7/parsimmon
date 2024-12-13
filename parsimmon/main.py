import argparse
import asyncio
import sys
import itertools
import threading
from pathlib import Path
import time

from anthropic import RateLimitError
from claude_api import ClaudeAPI


class LoadingSpinner:
    def __init__(self, message: str):
        self.message = message
        self.spinner = itertools.cycle(
            ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        )
        self.running = False

    def spin(self):
        while self.running:
            sys.stdout.write(f"\r{next(self.spinner)} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r\033[K")  # Clear line

    def __enter__(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        self.thread.join()


async def run_cli(path_to_urls: Path, query: str | None = None):
    claude = ClaudeAPI()

    def execute_query(prompt: str, retries: int = 3) -> str:
        for attempt in range(retries):
            try:
                with LoadingSpinner("Thinking..."):
                    return claude.query(prompt)
            except RateLimitError:
                if attempt == retries - 1:
                    raise
                time.sleep(2**attempt)
        return ""

    with open(path_to_urls) as f:
        urls = [url.strip() for url in f if url.strip()]

    with LoadingSpinner("Loading context..."):
        await claude.load_context(urls)

    if query:
        response = execute_query(query)
    else:
        prompt = input("\nQuery > ").strip()
        response = execute_query(prompt)

    print(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--path-to-urls", type=Path, required=True)
    parser.add_argument("-q", "--query", type=str)
    args = parser.parse_args()

    asyncio.run(run_cli(args.path_to_urls, args.query))


if __name__ == "__main__":
    main()
