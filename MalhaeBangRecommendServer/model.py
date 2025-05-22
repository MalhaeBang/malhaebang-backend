import re
import numpy as np
import pandas as pd

# 금액 파싱 관련 부분은 유지
KOREAN_NUMERAL_MAP = {
    '영': 0, '공': 0, '일': 1, '이': 2, '삼': 3, '사': 4, '오': 5,
    '육': 6, '칠': 7, '팔': 8, '구': 9
}

def normalize_money_spacing(text):
    return re.sub(r'(\d)\s*(억|천|백)', r'\1\2', text)

def korean_digits_to_number(k):
    result = ""
    for char in k:
        if char in KOREAN_NUMERAL_MAP:
            result += str(KOREAN_NUMERAL_MAP[char])
        else:
            result += char
    return result

def parse_korean_money(raw):
    raw = raw.strip().replace(" ", "")
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
        return int(min(parsed_amounts)), int(max(parsed_amounts))
    elif len(parsed_amounts) == 1:
        return 0, int(parsed_amounts[0])
    else:
        raise ValueError("금액을 1개 또는 2개 이상 입력해주세요.")

# 대출 추천 로직
def recommend_loan(df, text, user_profile_desc="", top_n=3):
    try:
        # 사용자 입력 파싱
        own_money, rent_price = parse_input(text)
        needed = rent_price - own_money
        needed = int(needed)

        filtered = df[df['키워드'].str.contains(user_profile_desc, case=False, na=False)].drop_duplicates()
        # print('filtered:', filtered[['대출명', '키워드', '한도']])

        if filtered.empty:
            return "조건에 맞는 대출 상품이 없습니다."

        # 금액 조건에 맞는 대출 상품 필터링
        filtered = filtered[(filtered["한도"] == 0) | (filtered["한도"] >= needed)].copy()
        # print('filtered:2', filtered[['대출명', '키워드', '한도']])
        if filtered.empty:
            return "조건에 맞는 대출 상품이 없습니다."

        # 유사도와 금리를 고려한 정렬
        filtered['최저금리'] = pd.to_numeric(filtered['최저금리'], errors='coerce')
        filtered['최저금리'] = filtered['최저금리'].fillna(0)
        # print('결측치처리완')

        filtered = filtered.sort_values(by=["한도", "최저금리"], ascending=[False, True])
        filtered.loc[filtered['한도'] == 0, '한도'] = '조회필요'
        if filtered.empty:
            return "조건에 맞는 대출 상품이 없습니다."
        # print('완료')
        # 상위 N개의 대출 상품 반환
        return filtered.head(top_n)

    except Exception as e:
        return f"오류 발생: {str(e)}"

# 추천 이유
def explain_loan_recommendation(recommended, user_input, profile, top_n=5):
    if isinstance(recommended, str):
        return recommended  # 오류 메시지 반환

    explanations = []
    own_money, rent_price = parse_input(user_input)
    needed = rent_price - own_money

    for index, row in recommended.iterrows():
        # 대출 상품의 특징과 관련된 상세한 설명
        특징 = row["특징"]
        금리 = row["최저금리"]
        한도 = row["한도"]

        # 추천 이유
        reason = f"이 상품은 선택하신 키워드({profile})와 대출 상품 특징을 바탕으로 추천되었습니다."


        if "청년" in profile:
            reason += " 청년 특화 상품으로, 젊은 층에 적합한 조건을 제공합니다."
        if "무주택" in profile:
            reason += " 무주택자를 위한 대출로, 주택을 구매하거나 임차할 때 유리한 조건입니다."
        if "신혼" in profile:
            reason += " 신혼부부 특화 상품으로, 결혼 초기 부담을 덜어주는 혜택이 있습니다."
        if "월세" in profile:
            reason += " 월세 대출에 최적화된 상품으로, 월세 부담을 줄이는 데 도움이 됩니다."
        if "전세사기" in profile:
            reason += " 전세사기 피해자를 위한 특화된 대출 상품으로, 전세금을 회복하는 데 도움이 되며, 피해 복구를 위한 상품입니다."
        if "대환" in profile:
            reason += " 기존 대출을 대환할 수 있는 상품으로, 금리를 낮추거나 상환 조건을 개선하여 장기적인 재정 부담을 줄여줍니다."
        if "농업" in profile:
            reason += " 농업 종사자를 위한 대출로, 농업에 필요한 자금을 지원하며, 농업 활동에 유리한 조건을 제공합니다."
        if "의료인" in profile:
            reason += " 의료인을 위한 특화된 대출 상품으로, 의료 분야에 종사하는 분들에게 유리한 조건을 제공합니다."
        if "공무원" in profile:
            reason += " 공무원 특화 상품으로, 유리한 대출 조건을 제공합니다."
        if "교직원" in profile:
            reason += " 교직원을 위한 대출로, 유리한 대출 조건을 제공합니다."
        if "사업자" in profile:
            reason += " 사업자를 위한 대출 상품으로, 사업을 운영하는 데 필요한 자금을 유리한 조건으로 지원합니다."
        if "군인" in profile:
            reason += " 군인 특화 대출로, 군 복무 중에도 혜택을 받을 수 있는 대출 상품입니다."
        if "금융인" in profile:
            reason += " 금융업 종사자를 위한 대출로, 금융 관련 업무에 종사하는 분들에게 유리한 조건을 제공합니다."
        if "퇴직" in profile:
            reason += " 퇴직 후 안정적인 재정 관리를 돕는 대출 상품입니다."
        if "가족" in profile:
            reason += " 가족을 위한 대출 상품으로, 가족을 부양하는 데 유리한 조건을 제공합니다."
        if "보증금" in profile:
            reason += " 보증금 대출로, 주택의 보증금을 지원하는 데에 특화된 대출 상품입니다."

        # 금리 및 한도에 대한 정보 제공
        if (금리 < 3.0) and (금리 != 0):
            reason += f" 특히 이 상품은 최저금리가 {금리:.2f}%로 낮아 장기적으로 상환 부담을 줄여줍니다."
        elif 금리 == 0:
            reason += f" 금리 산정 시 고객의 신용등급, 상환능력, 대출금액, 대출기간, 부수거래 실적 등이 반영되므로 영업점 및 고객센터 등을 통한 문의가 필요합니다."
        else:
            reason += f" 이 상품은 최저금리가 {금리:.2f}%로, 낮은 순으로 추천해드리고 있습니다."

        # 최종 설명에 링크 추가
        explanation = {
            "대출상품명": row["대출명"],
            "추천 이유": reason,
            "링크": row['제공기관 링크']
        }
        explanations.append(explanation)

    return explanations