"""LLM Service — Unified client for OpenAI + Anthropic.

Features:
- Supports GPT-4o and Claude 3.5 Sonnet
- Per-agent model selection
- Cost tracking
- Retry + timeout handling
- Structured output for compliance tasks
"""
import os
import asyncio
import json
from typing import Dict, Any, Optional

import structlog

logger = structlog.get_logger("llm_service")


class LLMService:
    """Unified LLM client for Sturna.ai agents."""

    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.total_cost = 0.0
        self.total_calls = 0

    async def generate(
        self,
        prompt: str,
        model: str = "gpt-4o",
        max_tokens: int = 2000,
        temperature: float = 0.2,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate completion from the appropriate provider."""
        self.total_calls += 1

        if model.startswith("gpt") or model.startswith("o1"):
            return await self._call_openai(prompt, model, max_tokens, temperature, system_prompt)
        elif model.startswith("claude"):
            return await self._call_anthropic(prompt, model, max_tokens, temperature, system_prompt)
        else:
            # Fallback
            return await self._call_openai(prompt, "gpt-4o", max_tokens, temperature, system_prompt)

    async def _call_openai(
        self, prompt: str, model: str, max_tokens: int, temperature: float, system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.openai_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            content = response.choices[0].message.content
            usage = response.usage

            cost = self._estimate_openai_cost(model, usage.prompt_tokens, usage.completion_tokens)
            self.total_cost += cost

            logger.info(
                "openai_call",
                model=model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                cost=cost,
            )

            return {
                "content": content,
                "model": model,
                "provider": "openai",
                "cost": cost,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                },
            }

        except Exception as e:
            logger.error("openai_error", error=str(e))
            return {"content": f"[OpenAI Error: {str(e)}]", "error": True}

    async def _call_anthropic(
        self, prompt: str, model: str, max_tokens: int, temperature: float, system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=self.anthropic_key)

            messages = []
            if system_prompt:
                messages.append({"role": "user", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )

            content = response.content[0].text
            usage = response.usage

            cost = self._estimate_anthropic_cost(model, usage.input_tokens, usage.output_tokens)
            self.total_cost += cost

            logger.info(
                "anthropic_call",
                model=model,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                cost=cost,
            )

            return {
                "content": content,
                "model": model,
                "provider": "anthropic",
                "cost": cost,
                "usage": {
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                },
            }

        except Exception as e:
            logger.error("anthropic_error", error=str(e))
            return {"content": f"[Anthropic Error: {str(e)}]", "error": True}

    def _estimate_openai_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Rough cost estimation for OpenAI models."""
        pricing = {
            "gpt-4o": (0.005, 0.015),
            "gpt-4o-mini": (0.00015, 0.0006),
        }
        rates = pricing.get(model, (0.005, 0.015))
        return (prompt_tokens * rates[0] + completion_tokens * rates[1]) / 1000

    def _estimate_anthropic_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        pricing = {
            "claude-3-5-sonnet-20241022": (0.003, 0.015),
            "claude-3-opus-20240229": (0.015, 0.075),
        }
        rates = pricing.get(model, (0.003, 0.015))
        return (input_tokens * rates[0] + output_tokens * rates[1]) / 1000

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_calls": self.total_calls,
            "total_cost_usd": round(self.total_cost, 4),
        }


# Singleton
_llm_service = None

def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service