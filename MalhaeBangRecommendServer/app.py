import re
import pandas as pd
from flask import Flask, render_template, request
from model import parse_input, recommend_loan, explain_loan_recommendation
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "http://localhost:8010", "https://malhaebang.link"]}}, supports_credentials=True)

# 대출 상품 정보 xlsx 파일 로드
# 우리, 국민, 하나은행 >> 전세대출
# 농협 >> 전부 : 키워드로 대출 추천하는 걸 구현하기에 좋은 상품 多

df = pd.read_excel('loan_info_0510.xlsx')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        user_profile = request.form['user_profile']

        # print(f"User input: {user_input}")
        # print(f"User profile: {user_profile}")

        try:
            # 사용자 입력값 파싱
            own_money, rent_price = parse_input(user_input)
            # print(f"Parsed values - Own money: {own_money}, Rent price: {rent_price}")
            own_money_copy = int(own_money/10000)
            if own_money_copy >= 10000: # 1억 넘으면
                tmp = int(own_money_copy//10000)
                tmp2 = int(own_money_copy - tmp * 10000)
                if tmp2 == 0:
                    own_money_result = f"{tmp}억 원"
                else: own_money_result = f"{tmp}억 {tmp2}만 원"
            else: own_money_result = f"{own_money_copy}만 원"

            rent_price_copy = int(rent_price/10000)
            if rent_price_copy >= 10000: # 1억 넘으면
                tmp = int(rent_price_copy//10000)
                tmp2 = int(rent_price_copy - tmp * 10000)
                if tmp2 == 0:
                    rent_price_result = f"{tmp}억 원"
                else: rent_price_result = f"{tmp}억 {tmp2}만 원"
            else: rent_price_result = f"{rent_price_copy}만 원"

            # 필요한 대출 금액 계산
            required_loan = rent_price - own_money
            required_loan_copy = int(required_loan/10000)
            if required_loan_copy >= 10000: # 1억 넘으면
                tmp = int(required_loan_copy//10000)
                tmp2 = int(required_loan_copy - tmp * 10000)
                if tmp2 == 0:
                    required_loan_result = f"{tmp}억 원"
                else: required_loan_result = f"{tmp}억 {tmp2}만 원"
            else: required_loan_result = f"{required_loan_copy}만 원"


            # 대출 상품 추천
            recommended_loans = recommend_loan(df, user_input, user_profile, top_n=5)
            # print(f"Recommended loans: {recommended_loans}")

            if isinstance(recommended_loans, str):
                return render_template('index.html', error=recommended_loans)

            # 추천 대출 상품 설명
            explanations = explain_loan_recommendation(recommended_loans, user_input, user_profile)
            # print(f"Explanations: {explanations}")

            # 결과 리스트 준비
            results = []
            for idx, loan in recommended_loans.iterrows():
                reason = next((item['추천 이유'] for item in explanations if item['대출상품명'] == loan['대출명']), '')
                if isinstance(loan['한도'], (int, float)):
                    pricelimit = int(loan['한도'] / 10000)
                    if pricelimit >= 10000: # 1억 넘는 거
                        hund_bill = pricelimit//10000
                        ten_bill = (pricelimit - hund_bill * 10000)
                        if ten_bill == 0:
                            pricelimit = f"{hund_bill}억 원"
                        else: pricelimit = f"{hund_bill}억 {ten_bill}만 원"
                    else:
                        pricelimit = f"{int(loan['한도'] / 10000)}만 원"
                else:
                    # '한도'가 '조회필요' 경우 그대로 출력
                    pricelimit = f"{loan['한도']}"

                if loan['최저금리'] == 0:
                    minrate = '조회필요'
                else:
                    minrate = f"{loan['최저금리']}"

                results.append({
                    'name': loan['대출명'],
                    'feature': loan['특징'],
                    'rate': f"{minrate}% ~ {loan['기본금리']}%",
                    'limit': pricelimit,
                    'period': loan['대출 기간'],
                    'link': loan['상세페이지 링크'],
                    'reason': reason
                })

            # 결과 페이지로 렌더링
            return render_template('index.html',
                                   own_money=own_money_result,
                                   rent_price=rent_price_result,
                                   required_loan=required_loan_result,
                                   results=results,
                                   user_input=user_input,
                                   user_profile=user_profile)

        except Exception as e:
            return render_template('index.html', error=f"입력 오류: {e}")

    return render_template('index.html')


@app.route('/recommend', methods=['GET'])
def show_recommend_page():
    return render_template('layout.html', content='recommend/recommend-index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)