import pandas as pd
import re
from sentence_transformers import SentenceTransformer, util
from transformers import BertTokenizer, BertModel 
import torch
from sklearn.metrics.pairwise import cosine_similarity

import os
os.environ["TRANSFORMERS_NO_TF"] = "2"

df = pd.read_excel("loan_info_0510.xlsx") 

# 문장 임베딩 모델 (사전 학습된 모델 사용)
model = SentenceTransformer("jhgan/ko-sroberta-multitask")

KOREAN_NUMERAL_MAP = {
    '영': 0, '공': 0, '일': 1, '이': 2, '삼': 3, '사': 4, '오': 5,
    '육': 6, '칠': 7, '팔': 8, '구': 9, '십': 10, '백': 100, '천': 1000,
    '만': 10000, '억': 10000
}

def normalize_money_spacing(text):
    return re.sub(r'(\d)\s*(억|천|백)', r'\1\2', text)

# 한글 숫자 → 아라비아 숫자
def korean_digits_to_number(k):
    result = ""
    for char in k:
        if char in KOREAN_NUMERAL_MAP:
            result += str(KOREAN_NUMERAL_MAP[char])
        else:import re

# 한글 숫자 변환기용 맵
KOREAN_NUMERAL_MAP = {
    '영': 0, '공': 0, '일': 1, '이': 2, '삼': 3, '사': 4, '오': 5,
    '육': 6, '칠': 7, '팔': 8, '구': 9
}

# 띄어쓰기 정규화 (예: '2 천' → '2천')
def normalize_money_spacing(text):
    return re.sub(r'(\d)\s*(억|천|백)', r'\1\2', text)

# 한글 숫자 → 아라비아 숫자
def korean_digits_to_number(k):
    result = ""
    for char in k:
        if char in KOREAN_NUMERAL_MAP:
            result += str(KOREAN_NUMERAL_MAP[char])
        else:
            result += char
    return result

# 금액 파싱 함수
def parse_korean_money(raw):
    raw = raw.strip().replace(" ", "")
    
    # 순수 한글 숫자 → 아라비아 숫자 치환 (예: '삼천오백' → '3천5백')
    raw = korean_digits_to_number(raw)

    amount = 0
    match = re.match(r'(?:(\d*)억)?(?:(\d*)천)?(?:(\d*)백)?', raw)
    if match:
        억 = match.group(1)
        천 = match.group(2)
        백 = match.group(3)

        if 억:
            amount += int(억 or "1") * 100_000_000
        if '천' in raw:
            amount += int(천 or "1") * 10_000_000
        if '백' in raw:
            amount += int(백 or "1") * 1_000_000

    return amount

def parse_input(text):
    text = normalize_money_spacing(text)

    # 핵심! '이억오천', '천오백' 같이 한 덩어리로 매치되게
    pattern = re.compile(
        r'([일이삼사오육칠팔구공영\d]*억\s*[일이삼사오육칠팔구공영\d]*천\s*[일이삼사오육칠팔구공영\d]*백?|'
        r'[일이삼사오육칠팔구공영\d]*억\s*[일이삼사오육칠팔구공영\d]*천?|'
        r'[일이삼사오육칠팔구공영\d]*천\s*[일이삼사오육칠팔구공영\d]*백?|'
        r'[일이삼사오육칠팔구공영\d]*천|'
        r'[일이삼사오육칠팔구공영\d]*백|'
        r'\d{4,})'
    )

    matches = pattern.findall(text)

    parsed_amounts = []
    for m in matches:
        if not m.strip():
            continue
        amount = parse_korean_money(m)
        if amount == 0:
            try:
                amount = int(re.sub(r'[^\d]', '', m))
            except:
                continue
        parsed_amounts.append(amount)
        if len(parsed_amounts) == 2:
            break

    if len(parsed_amounts) == 2:
        return min(parsed_amounts), max(parsed_amounts)
    elif len(parsed_amounts) == 1:
        return parsed_amounts[0], 0
    else:
        raise ValueError("금액을 1개 또는 2개 이상 입력해주세요.")


# ✅ 1. BERT 모델 로딩
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
bert_model = BertModel.from_pretrained("bert-base-uncased")

# BERT 모델을 통해 텍스트 임베딩 얻기
def get_embedding(text):
    tokens = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = bert_model(**tokens)
    # [CLS] 토큰의 임베딩을 사용
    return outputs.last_hidden_state[:, 0, :].numpy()

def match_keyword_to_profiles():
    original = {
        "청년": {'청년': 2.0, '무주택': 0.5, '임차인': 0.5, '월세': 0.5, '서민': 0.1, '보증금': 0.5, '오피스텔': 0.5, '만 34세 이하': 0.5},
        "무주택": {'임차인': 1.0, '예비세대주': 1.0, '서민': 0.1, '보증금': 0.3, '오피스텔': 0.3},
        "신혼부부": {'신혼': 2.0, '서민': 0.1, '오피스텔': 0.3, '보증금': 0.3, '예비세대주': 0.3, '세대주': 0.3},
        "직장인": {'직장인': 2.0, '임직원': 0.5, '새내기직장인': 0.3, '서민': 0.1},
        "농업종사자": {'농업': 2.0, '경영': 0.3},
        "의료인": {'의료인': 2.0, '개인': 0.1},
        "공무원": {'공무원': 2.0, '교직원': 0.5, '퇴직공무원': 0.5},
        "교직원": {'교직원': 2.0, '공무원': 0.5},
        "국가유공자": {'국가유공자': 2.0, '퇴직공무원': 0.5},
        "사업자": {'사업자': 2.0, '주택임대차': 0.1},
        "월세": {'월세': 2.0, '서민': 0.1, '오피스텔': 0.5},
        "군인": {'군': 2.0},
        "외국인": {'외국인': 2.0, '청년': 0.5, '무주택': 0.3},
        "퇴직": {'퇴직': 2.0, '국가유공자': 0.5},
        "금융인": {'금융': 2.0},
        "대환": {'대환': 2.0},
        '가족': {'가족': 2.0},
        '공공주택': {'공공주택': 2.0},
        '전세사기': {'전세사기': 2.0}
    }

    transposed = {}
    for profile, keywords in original.items():
        for kw, weight in keywords.items():
            if kw not in transposed:
                transposed[kw] = {}
            transposed[kw][profile] = weight

    return transposed

def match_profile_to_keywords(profile_desc):
    # match_keyword_to_profiles 함수에서 만든 transposed 사용
    keyword_to_profiles = match_keyword_to_profiles()
    result = {}
    for kw in keyword_to_profiles:
        if kw in profile_desc:
            for profile, weight in keyword_to_profiles[kw].items():
                result[kw] = result.get(kw, 0) + weight
    return result

def recommend_loan(text, user_profile_desc="", top_n=3):
    try:
        # 사용자 입력 파싱
        own_money, rent_price = parse_input(text)
        needed = rent_price - own_money

        # 사용자 프로필 키워드 매칭
        profile_keywords = match_profile_to_keywords(user_profile_desc)

        # 금액 조건에 맞는 대출 상품 필터링
        filtered = df[df["한도"] >= needed].copy()
        if filtered.empty:
            return "조건에 맞는 대출 상품이 없습니다."

        # 사용자 임베딩 계산
        user_embed = get_embedding(user_profile_desc)

        # 유사도 계산 함수 정의
        def weighted_similarity(row):
            특징 = row["특징"]
            
            # 사용자 입력 키워드가 특징에 포함되어 있으면 높은 유사도 부여
            if user_profile_desc and user_profile_desc in 특징:
                return 0.9995

            total_score = 0
            total_weight = 0
            for keyword, weight in profile_keywords.items():
                if keyword in 특징:
                    # 키워드 임베딩 계산
                    keyword_embed = get_embedding(keyword)
                    # 코사인 유사도 계산
                    sim = cosine_similarity(user_embed, keyword_embed)[0][0]
                    total_score += sim * weight
                    total_weight += weight
            return total_score / total_weight if total_weight > 0 else 0

        # 유사도 계산
        filtered["유사도"] = filtered.apply(weighted_similarity, axis=1)

        # 유사도가 0.3 이하인 항목 제거
        filtered = filtered[filtered["유사도"] > 0.3]

        if filtered.empty:
            return "조건에 맞는 대출 상품을 찾을 수 없습니다."

        # 유사도와 금리를 고려한 정렬
        filtered = filtered.sort_values(by=["유사도", "최저금리"], ascending=[False, True])

        # 상위 N개의 대출 상품 반환
        return filtered.head(top_n)
    except Exception as e:
        return f"오류 발생: {str(e)}"

# ✅ 5. 추천 이유 생성
def explain_loan_recommendation(recommended, user_input, profile, top_n=3):
    # 추천 로직 실행
    # recommended = recommend_loan(user_input, profile, top_n)

    # 추천된 대출 상품이 없을 경우 처리
    if isinstance(recommended, str):
        return recommended  # 오류 메시지 반환

    explanations = []

    # 추천된 대출 상품에 대해 설명 생성
    for index, row in recommended.iterrows():
        explanation = {
            "대출상품명": row["대출명"],
            "추천 이유": f"이 상품은 사용자 프로필({profile})과 대출 상품 특징({row['특징']})의 유사도({row['유사도']*100:.2f}%)와 최저 금리를 기준으로 추천되었습니다.",
            "유사도": row["유사도"],
            "링크": row['제공기관 링크']
        }
        explanations.append(explanation)

    return explanations