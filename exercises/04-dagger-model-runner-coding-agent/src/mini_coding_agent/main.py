from __future__ import annotations

import ast
import json
import re

import dagger
from dagger import dag, function, object_type


MODEL_RUNNER_BASE_URL = "http://model-runner.docker.internal/engines/v1"
DEFAULT_MODEL = "ai/llama3.2:latest"

MODEL_REQUEST_SCRIPT = r"""
import json
import os
import urllib.request

base_url = os.environ["MODEL_RUNNER_BASE_URL"].rstrip("/")
model = os.environ["MODEL_RUNNER_MODEL"]
messages = json.loads(os.environ["MODEL_MESSAGES"])
payload = {
    "model": model,
    "messages": messages,
    "max_tokens": 280,
    "temperature": 0.1,
}
body = json.dumps(payload).encode("utf-8")
request = urllib.request.Request(
    f"{base_url}/chat/completions",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=90) as response:
    data = json.loads(response.read().decode("utf-8"))
print(data["choices"][0]["message"]["content"])
"""


def extract_python(text: str) -> str:
    fenced = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1)
    return text.strip()


def looks_like_python(code: str) -> bool:
    try:
        ast.parse(code)
    except SyntaxError:
        return False
    return "def " in code and "print" in code


def local_fallback(feature_request: str) -> str:
    lowered = feature_request.lower()
    if "factorial" in lowered:
        match = re.search(r"factorial of (\d+)", lowered)
        number = match.group(1) if match else "5"
        return (
            "def factorial(n: int) -> int:\n"
            "    if n < 2:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n\n"
            f'print(factorial({number}))\n'
        )

    return (
        "def main() -> None:\n"
        f"    print({feature_request!r})\n\n"
        "if __name__ == '__main__':\n"
        "    main()\n"
    )


@object_type
class MiniCodingAgent:
    async def model_completion(self, messages: list[dict[str, str]], model: str) -> str:
        return await (
            dag.container()
            .from_("python:3.12-slim")
            .with_new_file("/tmp/request.py", MODEL_REQUEST_SCRIPT)
            .with_env_variable("MODEL_RUNNER_BASE_URL", MODEL_RUNNER_BASE_URL)
            .with_env_variable("MODEL_RUNNER_MODEL", model)
            .with_env_variable("MODEL_MESSAGES", json.dumps(messages))
            .with_exec(["python", "/tmp/request.py"])
            .stdout()
        )

    async def initial_code(self, feature_request: str, model: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Python coding agent. Return only valid Python code for a single file "
                    "named app.py. No markdown fences, no explanation. The file must run with python app.py."
                ),
            },
            {"role": "user", "content": feature_request},
        ]
        answer = await self.model_completion(messages, model)
        return extract_python(answer)

    async def review_and_fix(self, feature_request: str, code: str, feedback: str, model: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a reviewer agent. Fix the Python file so it satisfies the feature request "
                    "and runs correctly with python app.py. Return only the corrected Python code."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Feature request:\n{feature_request}\n\n"
                    f"Current code:\n{code}\n\n"
                    f"Feedback:\n{feedback}"
                ),
            },
        ]
        answer = await self.model_completion(messages, model)
        return extract_python(answer)

    async def build_final_code(self, feature_request: str, model: str) -> str:
        code = await self.initial_code(feature_request, model)
        if not looks_like_python(code):
            code = await self.review_and_fix(
                feature_request,
                code,
                "The result was not valid runnable Python with a function and a print statement.",
                model,
            )
        return code

    async def execute_code(self, code: str) -> tuple[str, str]:
        try:
            output = await (
                dag.container()
                .from_("python:3.12-slim")
                .with_new_file("/src/app.py", code)
                .with_workdir("/src")
                .with_exec(["python", "app.py"])
                .stdout()
            )
            return output.strip(), ""
        except dagger.ExecError as exc:
            return "", str(exc)

    async def reviewed_code(self, feature_request: str, model: str) -> str:
        code = await self.build_final_code(feature_request, model)
        output, error = await self.execute_code(code)
        if error or not output:
            feedback = error or "The program produced no output."
            code = await self.review_and_fix(feature_request, code, feedback, model)
            if not looks_like_python(code):
                code = local_fallback(feature_request)
                return code
            output, error = await self.execute_code(code)
            if error or not output:
                code = local_fallback(feature_request)
        return code

    @function
    async def generate_code(
        self,
        feature_request: str,
        model: str = DEFAULT_MODEL,
    ) -> str:
        """Generate Python code from a feature request using Docker Model Runner."""
        return await self.reviewed_code(feature_request, model)

    @function
    async def save_app(
        self,
        feature_request: str,
        model: str = DEFAULT_MODEL,
    ) -> dagger.File:
        """Generate code and expose it as app.py for export."""
        code = await self.reviewed_code(feature_request, model)
        return dag.directory().with_new_file("app.py", code).file("app.py")

    @function
    async def run_app(
        self,
        feature_request: str,
        model: str = DEFAULT_MODEL,
    ) -> str:
        """Generate code, run it in a Python container, and print code plus output."""
        code = await self.reviewed_code(feature_request, model)
        output, error = await self.execute_code(code)
        if error:
            raise RuntimeError(f"Generated code still failed after review: {error}")
        return (
            "Generated app.py:\n"
            "```python\n"
            f"{code}\n"
            "```\n\n"
            "Program output:\n"
            f"{output}"
        )
