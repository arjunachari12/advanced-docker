from __future__ import annotations

from typing import Annotated

import dagger
from dagger import DefaultPath, dag, function, object_type


@object_type
class GenaiAgentPipeline:
    source: Annotated[dagger.Directory, DefaultPath(".")]

    def agent_source(self) -> dagger.Directory:
        return self.source.directory("agent_app")

    @function
    def build_agent(self) -> dagger.Container:
        """Build the AI agent image from its Dockerfile."""
        return self.agent_source().docker_build()

    @function
    async def test_agent(self) -> str:
        """Run the agent unit tests inside a clean Python container."""
        return await (
            dag.container()
            .from_("python:3.12-slim")
            .with_directory("/src", self.agent_source())
            .with_workdir("/src")
            .with_exec(["python", "-m", "unittest", "test_agent.py"])
            .stdout()
        )

    @function
    async def run_agent(self, task: str = "Build and deploy a GenAI container safely.") -> str:
        """Run the built agent container with Ollama as the LLM backend."""
        return await (
            self.build_agent()
            .with_env_variable("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
            .with_env_variable("OLLAMA_MODEL", "qwen2.5:0.5b")
            .with_exec(["python", "/agent/agent.py", task])
            .stdout()
        )

    @function
    async def run_agent_offline(self, task: str = "Build and deploy a GenAI container safely.") -> str:
        """Run the built agent container without calling Ollama."""
        return await self.build_agent().with_exec(["python", "/agent/agent.py", "--offline", task]).stdout()

    @function
    async def run_agent_with_llm(
        self,
        task: str = "Build and deploy a GenAI container safely.",
        ollama_base_url: str = "http://host.docker.internal:11434",
        model: str = "qwen2.5:0.5b",
    ) -> str:
        """Run the agent container with a custom Ollama-compatible endpoint."""
        return await (
            self.build_agent()
            .with_env_variable("OLLAMA_BASE_URL", ollama_base_url)
            .with_env_variable("OLLAMA_MODEL", model)
            .with_exec(["python", "/agent/agent.py", task])
            .stdout()
        )

    @function
    async def dry_run_deploy(self, image: str = "ttl.sh/genai-agent-demo") -> str:
        """Show the deploy command without pushing to a registry."""
        await self.test_agent()
        await self.run_agent()
        return (
            "Dry-run deploy passed.\n"
            f"Next command: dagger call publish-agent --image={image}\n"
            "Use a real registry reference for a durable deployment."
        )

    @function
    async def publish_agent(self, image: str) -> str:
        """Test, build, and publish the agent image to a registry."""
        await self.test_agent()
        await self.run_agent()
        return await self.build_agent().publish(image)
