import re
import pandas as pd
from flask import Flask, request, jsonify, render_template
from model import parse_input, recommend_loan, explain_loan_recommendation
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Spring에서 요청할 수 있도록 CORS 허용

df = pd.read_excel('loan_info_0510.xlsx')

@app.route('/api/recommend', methods=['POST'])
def recommend_api():
    try:
        data = request.get_json()
        user_input = data.get('user_input')
        user_profile = data.get('user_profile')

        if not user_input or not user_profile:
            return jsonify({"error": "user_input과 user_profile이 모두 필요합니다."}), 400

        own_money, rent_price = parse_input(user_input)
        required_loan = rent_price - own_money

        recommended_loans = recommend_loan(user_input, user_profile, top_n=3)
        if isinstance(recommended_loans, str):
            return jsonify({
                "own_money": int(own_money / 10000),
                "rent_price": int(rent_price / 10000),
                "required_loan": int(required_loan / 10000),
                "results": [],
                "message": "조건에 맞는 대출 상품이 없습니다."
            }), 200

        explanations = explain_loan_recommendation(recommended_loans, user_input, user_profile)

        results = []
        for idx, loan in recommended_loans.iterrows():
            reason = next((item['추천 이유'] for item in explanations if item['대출상품명'] == loan['대출명']), '')
            results.append({
                'name': loan['대출명'],
                'feature': loan['특징'],
                'rate': f"{loan['최저금리']}% ~ {loan['기본금리']}%",
                'limit': int(loan['한도'] / 10000),
                'period': loan['대출 기간'],
                'link': loan['상세페이지 링크'],
                'reason': reason
            })

        return jsonify({
            "own_money": int(own_money / 10000),
            "rent_price": int(rent_price / 10000),
            "required_loan": int(required_loan / 10000),
            "results": results
        })

    except Exception as e:
        return jsonify({"error": f"서버 오류: {str(e)}"}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        user_profile = request.form.get('user_profile')

        # 분석 및 추천
        own_money, rent_price = parse_input(user_input)
        required_loan = rent_price - own_money

        recommended_loans = recommend_loan(user_input, user_profile, top_n=3)
        explanations = explain_loan_recommendation(recommended_loans, user_input, user_profile)

        results = []
        for idx, loan in recommended_loans.iterrows():
            reason = next((item['추천 이유'] for item in explanations if item['대출상품명'] == loan['대출명']), '')
            results.append({
                'name': loan['대출명'],
                'feature': loan['특징'],
                'rate': f"{loan['최저금리']}% ~ {loan['기본금리']}%",
                'limit': int(loan['한도'] / 10000),
                'period': loan['대출 기간'],
                'link': loan['상세페이지 링크'],
                'reason': reason
            })

        return render_template(
            'index.html',
            user_input=user_input,
            user_profile=user_profile,
            own_money=int(own_money / 10000),
            rent_price=int(rent_price / 10000),
            required_loan=int(required_loan / 10000),
            results=results
        )

    # GET 요청 처리
    return render_template('index.html')


# if __name__ == '__main__':
#     app.run(debug=True)
@app.route('/recommend', methods=['GET'])
def show_recommend_page():
    return render_template('layout.html', content='recommend/recommend-index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)