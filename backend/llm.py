import re
from typing import List, Dict, Any, Optional
from groq import Groq
from backend.config import settings

RETROMIND_SYSTEM_PROMPT = """You are RETROMIND, a retro-computing AI Knowledge Base Assistant.
Base your answers on the provided document context when available.
Cite your sources like [Source: filename, Page X].
Strictly NO EMOJIS anywhere in output."""

class LLMEngine:
    def __init__(self, provider: str = None, model_name: str = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.api_key = settings.GROQ_API_KEY or "ZZZZZZZZZZZZZZZ"
        self.model_name = model_name or settings.GROQ_MODEL
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def generate_answer(
        self, 
        query: str, 
        context: str, 
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        if not context or not context.strip():
            return "[SYSTEM NOTICE: NO MATCHING DATA FOUND IN RETROMIND KNOWLEDGE MATRIX. UNABLE TO VERIFY ANSWER FROM SOURCE DOCUMENTS.]"

        prompt_user = f"DOCUMENT CONTEXT:\n{context}\n\nUSER QUERY:\n{query}"
        
        messages = [{"role": "system", "content": RETROMIND_SYSTEM_PROMPT}]
        if chat_history:
            for msg in chat_history[-4:]:
                role = "assistant" if msg.get("role") == "assistant" else "user"
                messages.append({"role": role, "content": msg.get("content", "")})
        messages.append({"role": "user", "content": prompt_user})

        if self.client:
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.1,
                        max_tokens=1024
                    )
                    answer = response.choices[0].message.content
                    return self._sanitize(answer)
                except Exception as e:
                    last_err = str(e)
                    continue

            return f"[SYSTEM ERROR: GROQ INFERENCE FAILURE - {last_err}]"

        return self._generate_fallback_grounded_answer(query, context)

    def _sanitize(self, text: str) -> str:
        if not text:
            return ""
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub("", text).strip()

    _sanitize_response = _sanitize

    def _generate_fallback_grounded_answer(self, query: str, context: str) -> str:
        lines = context.split('\n')
        matched_lines = []
        query_words = [w.lower() for w in query.split() if len(w) > 3]

        for line in lines:
            if line.startswith("[DOCUMENT:"):
                continue
            line_lower = line.lower()
            if any(word in line_lower for word in query_words):
                matched_lines.append(line.strip())

        if matched_lines:
            summary = " ".join(matched_lines[:3])
            return f"[OFFLINE MATRIX EXTRACT] Based on retrieved record: {summary}"
        else:
            return "[SYSTEM NOTICE: NO MATCHING DATA FOUND IN RETROMIND KNOWLEDGE MATRIX. UNABLE TO VERIFY ANSWER FROM SOURCE DOCUMENTS.]"
