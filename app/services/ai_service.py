"""Wraps calls to the LLM provider (OpenAI by default, Gemini as fallback).

All prompt construction lives here so routers stay thin. Every generation
function returns already-validated JSON matching the shape the frontend
tab expects -- if the model returns malformed JSON we retry once, then
raise, rather than silently passing garbage to the client.
"""
import json
from openai import AsyncOpenAI
from app.core.config import get_settings

settings = get_settings()
_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


async def _complete_json(system: str, user: str, model: str = "gpt-4o-mini") -> dict:
    if _client is None:
        raise RuntimeError("OPENAI_API_KEY is not configured on the server.")
    resp = await _client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.4,
    )
    return json.loads(resp.choices[0].message.content)


async def generate_roadmap(topic: str) -> dict:
    system = (
        "You are a curriculum designer. Return strict JSON: "
        '{"steps": [{"title": str, "summary": str, "order": int}]}'
    )
    return await _complete_json(system, f"Topic: {topic}")


async def generate_theory(topic: str) -> dict:
    system = (
        "You are a patient teacher. Return strict JSON: "
        '{"sections": [{"heading": str, "body": str}], "common_mistakes": [str]}'
    )
    return await _complete_json(system, f"Explain: {topic}")


async def generate_cheat_sheet(topic: str) -> dict:
    system = 'Return strict JSON: {"items": [{"label": str, "detail": str}]}'
    return await _complete_json(system, f"Cheat sheet for: {topic}")


async def generate_mcqs(topic: str, difficulty: str, count: int = 10) -> dict:
    system = (
        "You are an exam writer. Return strict JSON: "
        '{"questions": [{"question": str, "options": [str,str,str,str], '
        '"correct_index": int, "explanation": str, '
        '"why_wrong": {"0": str, "1": str, "2": str, "3": str}}]}'
    )
    return await _complete_json(system, f"Topic: {topic}. Difficulty: {difficulty}. Count: {count}")


async def generate_coding_problem(topic: str, difficulty: str) -> dict:
    system = (
        "You are a coding interview problem setter. Return strict JSON: "
        '{"title": str, "prompt": str, '
        '"starter_code": {"python": str, "java": str, "javascript": str}, '
        '"visible_test_cases": [{"input": str, "output": str}], '
        '"hidden_test_cases": [{"input": str, "output": str}]}'
    )
    return await _complete_json(system, f"Topic: {topic}. Difficulty: {difficulty}")


async def review_submission(source_code: str, language: str, problem_prompt: str) -> dict:
    system = (
        "You are a senior engineer reviewing code. Return strict JSON: "
        '{"time_complexity": str, "space_complexity": str, '
        '"suggestions": [str], "style_notes": [str]}'
    )
    user = f"Problem: {problem_prompt}\n\nLanguage: {language}\n\nCode:\n{source_code}"
    return await _complete_json(system, user)


async def generate_interview_question(track: str, history: list[dict]) -> dict:
    system = (
        "You are conducting a live interview for the given track. "
        "Ask exactly one natural follow-up question based on the conversation so far. "
        'Return strict JSON: {"question": str}'
    )
    user = f"Track: {track}\nHistory: {json.dumps(history)}"
    return await _complete_json(system, user)


async def score_interview(track: str, transcript: list[dict]) -> dict:
    system = (
        "You are an interview evaluator. Return strict JSON: "
        '{"technical_score": float, "confidence_score": float, "grammar_score": float, '
        '"pronunciation_score": float, "communication_score": float, "suggestions": [str]}'
        " All scores are 0-100."
    )
    user = f"Track: {track}\nTranscript: {json.dumps(transcript)}"
    return await _complete_json(system, user)
