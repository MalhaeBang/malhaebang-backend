# main.py
from crawler import startCrawling
from filtered import filter_and_save_news as cluster_news
import pandas as pd
import os

def main():
    # 공유 디렉토리 생성
    os.makedirs("/app/shared_data", exist_ok=True)
    
    df = None
    try:
        df = startCrawling()
        if df is not None:
            df.to_csv("/app/shared_data/대표뉴스.csv", index=False)
            print("✅ 대표 뉴스 저장 완료 → /app/shared_data/대표뉴스.csv")
        else:
            print("❌ 크롤링 결과 없음")
    except Exception as e:
        print(f"❌ 크롤링 오류: {e}")

    # if df is not None:

    if df is not None and len(df) > 0:
        try:
            cluster_news(
                news_path="/app/shared_data/대표뉴스.csv",
                data_path="data.csv",
                cluster_output_path="/app/shared_data/clustered.csv",
                final_output_path="/app/shared_data/filtered_clustered_news.csv"
            )
            print("✅ 필터링 및 군집 완료 → /app/shared_data/filtered_clustered_news.csv")
        except Exception as e:
            print(f"❌ 군집+필터링 오류: {e}")
    else:
        print("⚠️ 크롤링 실패로 군집 및 필터링 생략")

if __name__ == "__main__":
    main()