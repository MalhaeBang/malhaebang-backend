from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from intent_classifier import classify_intent
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

# CORS 설정 - 도커 컴포즈의 웹 서버 도메인 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # malhaebang-web 서비스의 포트
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

def chat_with_gpt(user_input, client):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_input}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

@app.post("/query")
async def process_query(query: Query):
    try:
        intent = classify_intent(query.query)
        
        if intent == "매물 추천":
            result = handle_query(query.query)
            return result
        elif intent == "일상 대화":
            response = chat_with_gpt(query.query, client)
            return {"response": response, "houses": []}
        elif intent == "서비스 문의":
            return {
                "response": "💬 상담사와 연결해드릴까요? 더 궁금하신 점이 있으신가요?",
                "houses": []
            }
        else:
            return {
                "response": f"⚠️ '{intent}'로 분류된 질문은 현재 지원하지 않습니다.",
                "houses": []
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 