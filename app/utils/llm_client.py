from openai import OpenAI

from app.config.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_llm_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},  # or any model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content
