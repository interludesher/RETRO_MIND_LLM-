import pytest
from backend.llm import LLMEngine

def test_llm_empty_context_fallback():
    llm = LLMEngine()
    answer = llm.generate_answer(query="What is the project budget?", context="")
    assert "[SYSTEM NOTICE: NO MATCHING DATA FOUND IN RETROMIND KNOWLEDGE MATRIX." in answer

def test_llm_zero_emoji_sanitization():
    llm = LLMEngine()
    raw_with_emojis = "The project status is operational 🚀👍! [Source: specs.pdf, Page 1]"
    clean = llm._sanitize_response(raw_with_emojis)
    assert "🚀" not in clean
    assert "👍" not in clean
    assert "operational !" in clean or "operational" in clean

def test_llm_offline_fallback_generation():
    llm = LLMEngine()
    context = "[DOCUMENT: retro.pdf | PAGE: 1]\nRetroMind uses neon magenta #ff007f for accent borders."
    query = "What color does RetroMind use for accent borders?"
    answer = llm.generate_answer(query=query, context=context)
    assert answer is not None
    assert len(answer) > 0
    # Confirm no emojis present
    import re
    assert not re.search(r"[\U0001F600-\U0001F64F]", answer)
