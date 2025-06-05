import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def classify_intent(user_query):
    prompt = f"""
    너는 부동산 챗봇의 의도 분류기 역할을 맡는다.

    사용자가 입력한 문장의 의도를 반드시 아래 카테고리 중 하나로만 분류하라:
    1️⃣ 매물 추천 (예: 부동산 검색, 추천 요청, 조건 질의, 또는 '집', '방', '원룸', '거주지', '숙소' 같은 단어가 언급된 경우)
    2️⃣ 일상 대화 (예: 안녕, 잘 지냈어?, 오늘 날씨 좋네, 밥 먹었어?, 나는 강남역 좋아해)
    3️⃣ 서비스 문의 (예: 이 서비스는 뭐야?, 상담사 연결해줘, 고객센터 문의)
    4️⃣ 기타 (위 세 가지에 해당하지 않는 경우)

    💡 주의:
    - 사용자가 명시적으로 추천, 검색, 조건 요청을 말하지 않더라도,
    '집', '방', '원룸', '거주지', '숙소' 같은 단어가 포함되면 매물 추천으로 간주한다.
    - 단순히 ‘지명’이나 ‘역 이름’만 언급됐다고 해서 매물 추천으로 오해하지 말 것.
    - 출력은 반드시 아래 형식으로만 할 것: 의도: [매물 추천 | 일상 대화 | 서비스 문의 | 기타]

    예시:
    - "강남역 전세 2억 이하 추천해줘" → 의도: 매물 추천
    - "마포구에 80만원 이하 월세 있을까?" → 의도: 매물 추천
    - "좋은 방 어디 없을까" → 의도: 매물 추천
    - "우리 집 근처 역 알려줘" → 의도: 매물 추천
    - "나는 강남역을 좋아해" → 의도: 일상 대화
    - "용산역은 진짜 멋진 곳이야" → 의도: 일상 대화
    - "난 부동산에 관심 없어" → 의도: 일상 대화
    - "이 서비스는 어떻게 써?" → 의도: 서비스 문의
    - "야 ㅋㅋㅋ" → 의도: 일상 대화

    이제 사용자 입력을 분류하라.
    사용자 입력: "{user_query}"
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    result = response.choices[0].message.content.strip()
    #print(f"🔍 [의도 분류 결과]: {result}")

    # 의도 값만 깔끔히 추출
    match = re.search(r"의도:\s*(.+)", result)
    if match:
        intent = match.group(1).strip()
        return intent
    else:
        return "기타"
