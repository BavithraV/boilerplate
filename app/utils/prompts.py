RATING_PROMPT = """
You are an evaluator.

Evaluate the interaction between a DM (teacher) and a Reporter (learner).

DM Response:
{dm_response}

Reporter Response:
{reporter_response}

Give:
1. DM rating (0-10)
2. Reporter rating (0-10)
3. Feedback

Return response in JSON:
{{
  "dm_rating": 5,
  "reporter_rating": 4,
  "feedback": "string"
}}

"""
