from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import bleach

router = APIRouter()

async def send_to_lm_server(prompt: str, code: str):
    payload = {
        "model": "deepseek-coder-v2-lite-instruct",
        "messages": [{"role": "user", "content": prompt + "\n" + code}],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=860.0) as client:
        response = await client.post("http://127.0.0.1:1234/v1/chat/completions", json=payload)
        response.raise_for_status()
        response_json = response.json()

        allowed_tags = ["strong", "h2", "h3", "h4", "ul", "ol", "li", "br", "pre", "code"]
        ai_message = bleach.clean(response_json['choices'][0]['message']['content'], tags=allowed_tags)

    return ai_message

@router.post("/api/static-analysis")
async def static_analysis(request: Request):
    body = await request.json()
    code = body.get("code", "")
    prompt = """
    Conduct a detailed static analysis on the following code, identifying:
    - Potential syntax or runtime errors,
    - Code smells (e.g., duplicated code, overly complex structures),
    - Security vulnerabilities, if any,
    - Opportunities for improved readability, performance, or maintainability.
    Return insights with specific line references and recommendations for improvement.
"""
    response_message = await send_to_lm_server(prompt, code)
    return JSONResponse(content={"message": response_message})

@router.post("/api/bug-detection")
async def bug_detection(request: Request):
    body = await request.json()
    code = body.get("code", "")
    prompt = """Thoroughly analyze the provided code for potential bugs and security vulnerabilities.
     Consider all common programming pitfalls, including memory leaks, unhandled exceptions,
     and incorrect logic. Provide recommendations for fixes and explain the root cause of each identified issue."""

    response_message = await send_to_lm_server(prompt, code)
    return JSONResponse(content={"message": response_message})

@router.post("/api/code-completion")
async def code_completion(request: Request):
    body = await request.json()
    code = body.get("code", "")
    prompt = """Suggest optimized code completions or enhancements for the given code.
    - Focus on improving readability, performance, and maintainability while ensuring
    - compliance with industry best practices. If applicable, suggest alternative approaches
    - and provide a rationale for each suggestion."""
    response_message = await send_to_lm_server(prompt, code)
    return JSONResponse(content={"message": response_message})

@router.post("/api/test-case-generation")
async def test_case_generation(request: Request):
    body = await request.json()
    code = body.get("code", "")
    prompt = """Generate a suite of comprehensive test cases for the given code, including unit tests,
    edge cases, and scenarios that might cause the code to fail. Each test case should specify
    expected inputs and outputs, cover boundary conditions, and be formatted for ease of understanding."""
    response_message = await send_to_lm_server(prompt, code)
    return JSONResponse(content={"message": response_message})