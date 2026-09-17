import os
import json
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

CF_ACCOUNT_ID = os.environ["CLOUDFLARE_ACCOUNT_ID"]
CF_API_TOKEN = os.environ["CLOUDFLARE_API_TOKEN"]

# Swap this single line if you want a different Workers AI model later
CF_MODEL = "@cf/qwen/qwen3.8-27b"

CF_API_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"


def _extract_json(raw_text: str) -> dict:
    """
    Qwen (unlike gpt-4.1-mini) isn't guaranteed to return pure JSON.
    Strip common wrappers (```json ... ```, stray prose) before parsing.
    """
    text = raw_text.strip()

    # Strip markdown code fences if present
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        # Fallback: grab the first {...} block in the response
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)

    return json.loads(text)


async def generate_questions_intro(job_title, job_description, resume_text):
    SYSTEM_PROMPT = f"""
        You are an AI interview expert, who generates questions based on candidate's job_title, job_description, resume_text.
        You need to find out candidate's name, you need to generate an introduction text including candidate's name, you need to generate questions
        based on job_description, job_title, user's skills, years of experience from resume_text.

        Input:
            job_title: {job_title},
            job_description: {job_description},
            resume_text: {resume_text}

        Output:
            questions: array,
            introText: string,
            candidate_name: string

        Rules:
            - For Questions:
                a) Generate 2-3 questions.
                b) Consider years of experience to label difficulty of interview questions.
                c) Questions should be easy to hard manner.
                d) Questions related to only Skills mentioned in resume, job_description and job_title.
                e) Questions need to be small and to the point, and sometimes scenario based.
            - For Introduction Text:
                a) It's a simple text introduction which is going to be played on browser before starting the interview.
                b) Include candidate name, job title in the text.
                c) Add your own creativity.
            - For Candidate Name:
                a) Extract candidate name from resume, if candidate not found then consider candidate name as "Candidate".

        IMPORTANT: Respond with ONLY a single valid JSON object. No markdown fences, no explanation, no preamble.
        The JSON object must have exactly these keys: "questions" (array of strings), "introText" (string), "candidate_name" (string).

        Example 1:
        Input:
            job_title: Senior Java Developer
            job_description: Candidate should have experience on core java, spring boot, spring security etc......
            resume_text: Name- LoopKaka, ..., Skills: Java, Spring, Node JS, React Js, ....

        Output:
            {{"questions": ["What is java?", "What is the difference between List and Set"], "introText": "Hi LoopKaka, This is your mock interview for Senior Java Developer.", "candidate_name": "LoopKaka"}}
    """

    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Generate the JSON now."},
        ],
        "max_tokens": 1024,
        "reasoning_effort": "low",   # <-- ADD THIS LINE
    }

    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(CF_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        #print(json.dumps(data, indent=2))   # <-- ADD THIS TEMP DEBUG LINE


    if not data.get("success", False):
        raise RuntimeError(f"Cloudflare Workers AI error: {data.get('errors')}")

    result = data.get("result", {})
    choices = result.get("choices")

    if not choices:
        raise ValueError(f"No choices returned from Workers AI: {json.dumps(data)}")

    raw_text = choices[0]["message"]["content"]

    try:
        return _extract_json(raw_text)
    except (json.JSONDecodeError, AttributeError) as e:
        raise ValueError(f"Model did not return valid JSON. Raw output: {raw_text}") from e




#for report generation
async def generate_report(answers=None):
    if answers is None:
        answers = []

    SYSTEM_PROMPT = f"""
        You are an expert AI interviewer, who analyses the answers based on questions, and shares the feedback.
        You need to find out Score in percentage, Total Correct Answers and detailed areas of improvement (not more than 5 points).

        Input: {answers}

        Input Structure:
        answers is an array, which will have objects.
        - array[]
            - object
                - question: string = it'll contain question in string.
                - answer: string | None = if skip is true then answer will be None else answer will have string.
                - skip: bool = if user gives answer then skip = False else skip = True

        Output Structure:
        I need output in JSON format, and it'll contain the object below:
        - Object
            - score: string = It should calculate percentage from correct (answer / total question) % 100
            - correct_answer: number = number of correct answers
            - improvment_area: array of string = it'll contain areas of improvement. not more than 5 points.

        Rule:
         - Don't be so strict to evaluate the answer.
         - Consider the answer correct if candidate answered at least 70%. But provide the feedback.
         - If candidate didn't answer anything then mark score 0%, correct_answer 0 and improvment_area as it is provided.

        IMPORTANT: Respond with ONLY a single valid JSON object. No markdown fences, no explanation, no preamble.
        The JSON object must have exactly these keys: "score" (string), "correct_answer" (number), "improvment_area" (array of strings).
    """

    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Generate the JSON now."},
        ],
        "max_tokens": 1024,
        "reasoning_effort": "low",
    }

    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(CF_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    if not data.get("success", False):
        raise RuntimeError(f"Cloudflare Workers AI error: {data.get('errors')}")

    result = data.get("result", {})
    choices = result.get("choices")

    if not choices:
        raise ValueError(f"No choices returned from Workers AI: {json.dumps(data)}")

    raw_text = choices[0]["message"]["content"]

    try:
        return _extract_json(raw_text)
    except (json.JSONDecodeError, AttributeError) as e:
        raise ValueError(f"Model did not return valid JSON. Raw output: {raw_text}") from e

    