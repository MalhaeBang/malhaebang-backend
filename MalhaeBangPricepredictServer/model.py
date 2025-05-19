import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import base64
from adjustText import adjust_text
import io
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
import matplotlib as mpl

plt.rc('font', family='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False

# 데이터 필터링 함수 - 군집
def filter_rows_by_tag(df, tag_input, label_input):
    compare = df.copy()

    # 지역 필터링
    if tag_input:
        if tag_input in ['전국', '수도권']:
            compare = compare[compare['지역'].isin(['전국', '수도권', '서울'])]
        elif tag_input == '서울':
            compare = compare[compare['지역'].isin(['서울', '서울 강남지역', '서울 강북지역'])]
        elif tag_input in ['서울 강남지역', '서울 강남지역 서남권', '서울 강남지역 동남권']:
            compare = compare[compare['지역'].isin(['서울 강남지역', '서울 강남지역 서남권', '서울 강남지역 동남권'])]
        elif tag_input in ['서울 강북지역', '서울 강북지역 도심권', '서울 강북지역 동북권', '서울 강북지역 서북권']:
            compare = compare[compare['지역'].isin(['서울 강북지역', '서울 강북지역 도심권', '서울 강북지역 동북권', '서울 강북지역 서북권'])]
        else:
            compare = compare[compare['지역'] == tag_input]

    # 라벨 필터링 (문자열로 변환 후 필터링)
    if label_input:
        compare['면적'] = compare['면적'].astype(str)  # 문자열로 변환
        compare = compare[compare['면적'].str.strip() == label_input.strip()]

    # print("[DEBUG] 최종 필터링된 데이터 shape:", compare.shape)
    return compare

# 데이터 필터링 함수
def filter_rows_exact(df, tag_input, label_input):
    compare = df.copy()
    if tag_input:
        compare = compare[compare['지역'] == tag_input]
    if label_input:
        compare['면적'] = compare['면적'].astype(str)
        compare = compare[compare['면적'].str.strip() == label_input.strip()]
    # print("[DEBUG] (정확히 일치) 최종 필터링된 데이터 shape:", compare.shape)
    return compare

# 라인플랏 
def create_line_plot(df):
    plt.figure(figsize=(10, 6))
    
    # 날짜 컬럼 추출 및 datetime 변환
    date_columns = df.columns[2:]
    date_list = [datetime.strptime(col, "%Y-%m-%d") for col in date_columns]
    
    for idx, row in df.iterrows():
        plt.plot(date_list, row[date_columns], label=row['지역'])
    
    # 6개월 간격 마커 및 값 추가
    major_locator = mdates.MonthLocator(interval=24)
    major_formatter = mdates.DateFormatter('%Y-%m')

    plt.gca().xaxis.set_major_locator(major_locator)
    plt.gca().xaxis.set_major_formatter(major_formatter)

    texts = []

    # 마커 및 값 표시
    for idx, row in df.iterrows():
        for i, date in enumerate(date_list):
            if i % 24 == 0:  # 6개월 간격
                # 마커 간격을 주기 위해 x축 위치를 조금씩 이동
                offset = 0.05 * (i % 2)
                plt.scatter(date + pd.Timedelta(days=offset), row[date_columns[i]], color='black', zorder=5, s=10)
                text = plt.text(date + pd.Timedelta(days=offset), row[date_columns[i]], f'{row[date_columns[i]]:.2f}', 
                                color='black', fontsize=7, ha='center', va='bottom', zorder=10)
                texts.append(text)

    adjust_text(texts) # 텍스트 겹침 방지

    plt.text(
        0.99, 0.05,
        '데이터 출처: 한국부동산원  기준시점: 25.03.31.=100.0',
        transform=plt.gca().transAxes,
        fontsize=9,
        ha='right',
        va='top',
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="gray", alpha=0.7)
    )

    plt.xticks(rotation=45)
    plt.title('전세가격지수 추세')
    plt.xlabel('날짜')
    plt.ylabel('전세가격지수')
    plt.legend()

    # 이미지 저장
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

# 오피스텔 시각화
def create_office_plot(df, title):
    plt.figure(figsize=(10, 6))
    for col in df.columns[1:]:
        plt.plot(df['날짜'], df[col], label=col)
    plt.title(title)
    plt.xlabel('날짜')
    plt.ylabel('가격')
    plt.legend()
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

# 차트 확대 버전
def create_actual_vs_pred_zoom_plot(df_actual, df_pred, region, label, months=12):
    actual = filter_rows_exact(df_actual, region, label)
    pred = filter_rows_exact(df_pred, region, label)
    if actual.empty or pred.empty:
        return None

    def parse_date(date_str):
        if len(date_str) == 7:
            return datetime.strptime(date_str, "%Y-%m")
        elif len(date_str) == 10:
            return datetime.strptime(date_str, "%Y-%m-%d")
        else:
            raise ValueError(f"지원하지 않는 날짜 형식: {date_str}")

    pred_date_columns = pred.columns[2:]
    pred_date_list = [parse_date(col) for col in pred_date_columns]
    pred_slice_cols = pred_date_columns[-months:]
    pred_slice_dates = pred_date_list[-months:]

    plt.figure(figsize=(12, 6))
    for idx, row in actual.iterrows():
        # 실제 컬럼에 존재하는 것만 슬라이싱
        available_cols = [col for col in pred_slice_cols if col in row.index]
        available_dates = pred_slice_dates[-len(available_cols):] if available_cols else []
        if available_cols and available_dates:
            plt.plot(available_dates, row[available_cols], label=f"{row['지역']} 실측 (zoom)", color='blue')

    for idx, row in pred.iterrows():
        available_cols = [col for col in pred_slice_cols if col in row.index]
        available_dates = pred_slice_dates[-len(available_cols):] if available_cols else []
        if available_cols and available_dates:
            plt.plot(available_dates, row[available_cols], label=f"{row['지역']} 예측 (zoom)", color='red', linestyle='--')

    plt.title(f"{region} {label} 예측구간 확대")
    plt.xlabel('날짜')
    plt.ylabel('전세가격지수')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True) 
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url_zoom = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return plot_url_zoom

# 예측 함수
def create_actual_vs_pred_plot(df_actual, df_pred, region, label):
    """
    df_actual: 실측 데이터 DataFrame
    df_pred: 예측 데이터 DataFrame
    region: 지역명 (str)
    label: 면적 라벨 (str)
    """

    def parse_date(date_str):
        if len(date_str) == 7:
            # 'YYYY-MM'
            return datetime.strptime(date_str, "%Y-%m")
        elif len(date_str) == 10:
            # 'YYYY-MM-DD'
            return datetime.strptime(date_str, "%Y-%m-%d")
        else:
            raise ValueError(f"지원하지 않는 날짜 형식: {date_str}")

    # region, label로 데이터 필터링
    actual = filter_rows_exact(df_actual, region, label)
    pred = filter_rows_exact(df_pred, region, label)
    
    if actual.empty or pred.empty:
        return None

    plt.figure(figsize=(12, 6))
    
    date_columns = actual.columns[2:]
    date_list = [parse_date(col) for col in date_columns]
    
    # 실측값 플롯
    for idx, row in actual.iterrows():
        plt.plot(date_list, row[date_columns], label=f"{row['지역']} 실측", color='blue')
    
    # 예측값 플롯
    pred_date_columns = pred.columns[2:]
    pred_date_list = [parse_date(col) for col in pred_date_columns]

    for idx, row in pred.iterrows():
        plt.plot(pred_date_list, row[pred_date_columns], label=f"{row['지역']} 예측", color='red', linestyle='--')
    
    plt.title(f"{region} {label} 실측/예측 전세가격지수")
    plt.xlabel('날짜')
    plt.ylabel('전세가격지수')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True) 
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return plot_url

# 실측 3개월 + 예측 3개월
def create_actual_vs_pred_6months_plot(df_actual, df_pred, region, label):
    actual = filter_rows_exact(df_actual, region, label)
    pred = filter_rows_exact(df_pred, region, label)
    if actual.empty or pred.empty:
        return None

    def parse_date(date_str):
        if len(date_str) == 7:
            return datetime.strptime(date_str, "%Y-%m")
        elif len(date_str) == 10:
            return datetime.strptime(date_str, "%Y-%m-%d")
        else:
            raise ValueError(f"지원하지 않는 날짜 형식: {date_str}")

    actual_date_columns = actual.columns[2:]
    pred_date_columns = pred.columns[2:]

    # 날짜 정렬
    actual_dates = [parse_date(col) for col in actual_date_columns]
    pred_dates = [parse_date(col) for col in pred_date_columns]

    actual_last3_cols = actual_date_columns[-3:]
    actual_last3_dates = actual_dates[-3:]

    pred_first3_cols = pred_date_columns[:3]
    pred_first3_dates = pred_dates[:3]

    plt.figure(figsize=(10, 6))

    # --- 실측값 플롯 (첫 번째 행만) ---
    row = actual.iloc[0]
    y_actual = row[actual_last3_cols].tolist()
    plt.plot(actual_last3_dates, y_actual, color='blue', label=f"{row['지역']} 실측")
    for i, (x, y) in enumerate(zip(actual_last3_dates, y_actual)):
        if i % 2 == 0:
            plt.scatter(x, y, color='blue', marker='o', zorder=5)

    # --- 예측값 플롯 (첫 번째 행만) ---
    row_pred = pred.iloc[0]
    y_pred = row_pred[pred_first3_cols].tolist()
    plt.plot(pred_first3_dates, y_pred, color='red', linestyle='--', label=f"{row_pred['지역']} 예측")
    for i, (x, y) in enumerate(zip(pred_first3_dates, y_pred)):
        if i % 2 == 0:
            plt.scatter(x, y, color='red', marker='o', zorder=5)

    # 실측 마지막값과 예측 첫값을 선으로 연결
    plt.plot([actual_last3_dates[-1], pred_first3_dates[0]],
             [y_actual[-1], y_pred[0]],
             color='gray', linestyle=':', alpha=0.5)

    plt.title(f"{region} {label} 최근 6개월 (실측 3 + 예측 3)")
    plt.xlabel('날짜')
    plt.ylabel('전세가격지수')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url_zoom = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url_zoom


def create_plotly_actual_vs_pred_plot(df_actual, df_pred, region, label):
    actual = filter_rows_exact(df_actual, region, label)
    pred = filter_rows_exact(df_pred, region, label)

    if actual.empty or pred.empty:
        return None

    def parse_date(date_str):
        if len(date_str) == 7:
            return datetime.strptime(date_str, "%Y-%m")
        elif len(date_str) == 10:
            return datetime.strptime(date_str, "%Y-%m-%d")
        else:
            raise ValueError(f"지원하지 않는 날짜 형식: {date_str}")

    # 날짜 컬럼 추출
    actual_date_columns = actual.columns[2:]
    pred_date_columns = pred.columns[2:]
    actual_dates = [parse_date(col) for col in actual_date_columns]
    pred_dates = [parse_date(col) for col in pred_date_columns]

    # Plotly 그래프 생성
    fig = go.Figure()

    # 실측 데이터 추가
    for idx, row in actual.iterrows():
        fig.add_trace(go.Scatter(
            x=actual_dates,
            y=row[actual_date_columns],
            mode='lines+markers',
            name=f"{row['지역']} 실측",
            line=dict(color='blue'),
            marker=dict(size=6),
            hovertemplate='날짜: %{x|%Y-%m-%d}<br>지수: %{y:.2f}<extra></extra>'
        ))

    # 예측 데이터 추가
    for idx, row in pred.iterrows():
        fig.add_trace(go.Scatter(
            x=pred_dates,
            y=row[pred_date_columns],
            mode='lines+markers',
            name=f"{row['지역']} 예측",
            line=dict(color='red', dash='dash'),
            marker=dict(size=6),
            hovertemplate='날짜: %{x|%Y-%m-%d}<br>예측지수: %{y:.2f}<extra></extra>'
        ))

    fig.update_layout(
        title=f"{region} {label} 실측/예측 전세가격지수",
        xaxis_title='날짜',
        yaxis_title='전세가격지수',
        xaxis=dict(tickformat='%Y-%m'),
        template='plotly_white',
        hovermode='x unified',
        legend=dict(x=0, y=1)
    )

    # HTML로 렌더링 가능한 JSON 반환
    return json.dumps(fig, cls=PlotlyJSONEncoder)
