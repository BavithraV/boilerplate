from openai import OpenAI

from app.config.settings import settings


def get_llm_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def get_llm_response(prompt: str) -> str:
    client = get_llm_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content
