# app.py
from flask import Flask, render_template, request
import pandas as pd
import random
import os

app = Flask(__name__)

@app.route('/')
def index():
    csv_path = "/app/shared_data/filtered_clustered_news.csv"
    if not os.path.exists(csv_path):
        return "❌ filtered_clustered_news.csv 파일이 없습니다.", 500

    df = pd.read_csv(csv_path).dropna(subset=["title", "url", "content", "img"])
    main_news = df.head(3)
    exclude_urls = main_news["url"].tolist()

    main_list = []
    for _, row in main_news.iterrows():
        summary = ' '.join(row["content"].replace('\n', ' ').split())
        summary = summary[:70] + "…" if len(summary) > 70 else summary
        main_list.append({
            "title": row["title"],
            "url": row["url"],
            "img": str(row["img"]).split(",")[0] if pd.notna(row["img"]) else "/static/default.jpg",
            "summary": summary
        })

    return render_template("index.html", main=main_list, exclude_urls=exclude_urls)

@app.route('/more')
def more():
    csv_path = "/app/shared_data/filtered_clustered_news.csv"
    if not os.path.exists(csv_path):
        return "❌ filtered_clustered_news.csv 파일이 없습니다.", 500

    df = pd.read_csv(csv_path).dropna(subset=["title", "url", "content", "img"])
    exclude_urls = request.args.getlist('exclude_urls')

    # ❗ 페이지 번호 받아오기 (없으면 기본 1페이지)
    page = int(request.args.get('page', 1))
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page

    filtered_df = df[~df["url"].isin(exclude_urls)]
    total_pages = (len(filtered_df) + per_page - 1) // per_page  # 올림

    page_df = filtered_df.iloc[start:end]

    more_list = []
    for _, row in page_df.iterrows():
        summary = ' '.join(row["content"].replace('\n', ' ').split())
        summary = summary[:80] + "..." if len(summary) > 80 else summary
        more_list.append({
            "title": row["title"],
            "url": row["url"],
            "img": row["img"].split(",")[0] if row["img"] else "",
            "summary": summary
        })

    return render_template("more.html", news_list=more_list, page=page, total_pages=total_pages)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)