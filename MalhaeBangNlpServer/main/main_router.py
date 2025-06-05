from intent_classifier import classify_intent
from search_module_final_v2 import handle_query
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

# CORS 설정 - 개발 환경에서는 모든 도메인 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 사용자 쿼리를 받을 데이터 모델
class UserQuery(BaseModel):
    query: str

# 사용자 쿼리 처리 엔드포인트
@app.post("/query")
async def process_query(user_query: UserQuery):
    user_input = user_query.query

    print(f"\n📥 사용자 입력: {user_input}")

    intent = classify_intent(user_input)
    print(f"🔍 [의도 분류 결과]: {intent}")

    if intent == "매물 추천":
        # 매물 추천 로직 호출 및 결과 반환
        # handle_query 함수가 어떤 값을 반환하는지 확인 필요
        # 현재 handle_query는 print만 하고 반환값이 없는 것으로 보입니다.
        # 프론트엔드에 결과를 보내려면 handle_query에서 결과를 반환해야 합니다.
        # 임시로 성공 메시지만 반환하도록 하겠습니다.
        house_list = handle_query(user_input)
        return {"intent": intent, "response": house_list} # 실제 검색 결과로 변경 필요
    elif intent == "일상 대화":
        # 일상 대화 로직 호출 및 결과 반환
        # chat_with_gpt 함수도 현재 print만 하고 반환값이 없습니다.
        # 프론트엔드에 결과를 보내려면 chat_with_gpt에서 결과를 반환해야 합니다.
        # 임시로 GPT 응답을 반환하도록 하겠습니다.
        gpt_response = chat_with_gpt_return(user_input, client) # 반환하도록 함수 수정 필요
        return {"intent": intent, "response": gpt_response}
    elif intent == "서비스 문의":
        return {"intent": intent, "response": "💬 상담사와 연결해드릴까요? 더 궁금하신 점이 있으신가요?"}
    else:
        return {"intent": intent, "response": "매물과 관련된 조건을 자세하게 입력해주시면 정확한 추천을 받을 수 있어요! 🏠"}


# chat_with_gpt 함수를 수정하여 응답을 반환하도록 변경 (임시)
def chat_with_gpt_return(user_input, client):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_input}],
        temperature=0.7
    )
    reply = response.choices[0].message.content.strip()
    print(f"\n🤖 GPT 응답: {reply}")
    return reply

# handle_query 함수도 결과를 반환하도록 수정 필요 (여기서는 임시로 pass)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)