from intent_classifier import classify_intent
from search_module_final_v2 import handle_query
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def chat_with_gpt(user_input, client):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_input}],
        temperature=0.7
    )
    reply = response.choices[0].message.content.strip()
    print(f"\n🤖 GPT 응답: {reply}")

def main():
    while True:
        user_input = input("\n📥 사용자 입력 (exit 입력 시 종료): ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 종료합니다.")
            break

        intent = classify_intent(user_input)
        if intent == "매물 추천":
            handle_query(user_input)  # ← 여기 client 제거
        elif intent == "일상 대화":
            chat_with_gpt(user_input, client)
        elif intent == "서비스 문의":
            print("💬 상담사와 연결해드릴까요? 더 궁금하신 점이 있으신가요?")
        else:
            print(f"매물과 관련된 조건을 자세하게 입력해주시면 정확한 추천을 받을 수 있어요! 🏠")
if __name__ == "__main__":
    main()
