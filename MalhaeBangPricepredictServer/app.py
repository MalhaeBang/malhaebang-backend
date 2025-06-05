from flask import Flask, render_template, request, make_response, render_template_string, send_file
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import platform
import os
import json
import base64

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Image, Spacer, PageBreak, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

from model import (
    filter_rows_by_tag,
    filter_rows_exact,
    create_line_plot,
    create_office_plot,
    create_actual_vs_pred_zoom_plot,
    create_actual_vs_pred_plot,
    create_actual_vs_pred_6months_plot,
    create_plotly_actual_vs_pred_plot,

)


plt.rcParams['axes.unicode_minus'] = False

app = Flask(__name__)

# 폰트 로드
pdfmetrics.registerFont(TTFont('NanumGothic', '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'))
pdfmetrics.registerFont(TTFont('NanumGothic-Bold', '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf'))

# CSV 파일 로드
df = pd.read_csv('static/weekly_price.csv', encoding='utf-8')
pred = pd.read_csv('static/weekly_price_pred.csv', encoding='utf-8')

# JSON 파일 로드
office_monthly = pd.read_json('static/office_monthly.json')
office_monthly = pd.read_json('static/office_yearly.json')

# 지역 및 라벨 목록 추출
regions = df['지역'].dropna().unique().tolist()
labels = df['면적'].dropna().unique().tolist()

label_mapping = {
        '1': '40㎡초과 ~ 60㎡이하',
        '2': '60㎡초과 ~ 85㎡이하',
        '3': '85㎡초과 ~ 102㎡이하',
        '4': '102㎡초과 ~ 135㎡이하',
        '5': '135㎡초과'
    }

# 1. 지역별 아파트 전세가격지수 추이
@app.route('/', methods=['GET', 'POST'])
def index():
    selected_region = request.form.get('region')
    selected_label = request.form.get('label')

    if not selected_label:
        selected_label = ''

    labels = df['면적'].astype(str).unique().tolist()

    zipped_labels = list(zip(labels, [label_mapping.get(label, label) for label in labels]))
    converted_labels = [label_mapping.get(label, label) for label in labels]

    filtered_df = df

    if selected_region and selected_label:
        # print(f"[DEBUG] 선택된 지역: {selected_region}, 라벨: {selected_label}")
        filtered_df = filter_rows_by_tag(df, selected_region, selected_label)
        # print(f"[DEBUG] 필터링 후 shape: {filtered_df.shape}")
        # print(f"[DEBUG] 컬럼명: {filtered_df.columns.tolist()}")
    else:
        filtered_df = pd.DataFrame()

    table = filtered_df.head(10).to_html(classes='table table-bordered', index=False) if not filtered_df.empty else "<p>데이터 없음</p>"

    plot_url = None
    if not filtered_df.empty:
        plot_url = create_line_plot(filtered_df)

    # `office_monthly` 또는 `office_yearly`를 json_data로 대신 사용
    json_data = office_monthly

    return render_template(
        'index.html',
        regions=regions,
        selected_region=selected_region,
        selected_label=selected_label,
        zipped_labels=zipped_labels,
        table=filtered_df.to_html(classes='table table-bordered') if not filtered_df.empty else None,
        plot_url=plot_url,
        json_data=json_data.to_html(classes='table table-bordered', index=False) if not json_data.empty else None
    )

# 2. 전세가격지수 예측
@app.route('/plotly-chart', methods=['GET', 'POST'], strict_slashes=False)
def plotly_chart():
    labels = df['면적'].astype(str).unique().tolist()
    zipped_labels = list(zip(labels, [label_mapping.get(label, label) for label in labels]))
    
    selected_region = request.args.get('region', '서울')
    selected_label = request.args.get('label', '1')

    selected_label_kor = label_mapping.get(selected_label, selected_label)

    plot_json = create_plotly_actual_vs_pred_plot(df, pred, selected_region, selected_label)
    
    
    return render_template(
        'plotly_chart.html',
        plot_json=plot_json,
        regions=regions,
        selected_region=selected_region,
        selected_label=selected_label,
        selected_label_kor=selected_label_kor,
        zipped_labels=zipped_labels
    )

# 3. 전세가격지수 비교 보고서
@app.route('/forecast', methods=['GET', 'POST'], strict_slashes=False)
def actual_vs_pred():
    labels = df['면적'].astype(str).unique().tolist()
    zipped_labels = [(label, label_mapping.get(label, label)) for label in labels]

    selected_region = request.form.get('region', request.args.get('region', '서울')) # 기본값 '서울'
    selected_region2 = request.form.get('region2', request.args.get('region2', '전국')) # 기본값 '전국'
    selected_label = request.form.get('label', request.args.get('label', '1'))
    selected_label_kor = label_mapping.get(selected_label, selected_label)

    filtered_df = df[((df['지역'] == selected_region) | (df['지역'] == selected_region2)) & (df['면적'].astype(str) == selected_label)]
    filtered_df = filtered_df.set_index(filtered_df.columns[0])

    # 여러 년도 선택
    selected_years = request.form.getlist('years[]')

    if selected_years:
        # 컬럼명에 선택된 연도 중 하나라도 포함된 컬럼만 남김
        filtered_df = filtered_df.loc[:, filtered_df.columns[filtered_df.columns.str.contains('|'.join(selected_years))]]

    plot_url = create_actual_vs_pred_plot(df, pred, selected_region, selected_label)
    plot_url_zoom = create_actual_vs_pred_6months_plot(df, pred, selected_region, selected_label)
    plot_url2 = create_actual_vs_pred_plot(df, pred, selected_region2, selected_label)
    plot_url_zoom2 = create_actual_vs_pred_6months_plot(df, pred, selected_region2, selected_label)

    filtered_df_html = filtered_df.to_html(classes="table table-bordered table-striped", index=True)

    return render_template(
        'forecast.html',
        plot_url=plot_url,
        plot_url_zoom=plot_url_zoom,
        plot_url2=plot_url2,
        plot_url_zoom2=plot_url_zoom2,
        regions=regions,
        labels=labels,
        selected_region=selected_region,
        selected_region2=selected_region2,
        selected_label=selected_label,
        selected_label_kor=selected_label_kor,
        zipped_labels=zipped_labels,
        df_html=filtered_df_html,
        selected_years=selected_years
    )


# 3-2. 전세가격지수 비교 보고서 pdf 추출
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    # --- 입력값 수집 ---
    selected_region = request.form.get('selected_region')
    selected_region2 = request.form.get('selected_region2')
    selected_label = request.form.get('selected_label')
    selected_label_kor = request.form.get('selected_label_kor')
    selected_years = request.form.getlist('selected_years')

    plot_urls = [
        request.form.get('plot_url'),
        request.form.get('plot_url_zoom'),
        request.form.get('plot_url2'),
        request.form.get('plot_url_zoom2')
    ]

    # --- 스타일 설정 ---
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('KoreanTitle', parent=styles['Title'], fontName='NanumGothic-Bold', fontSize=18, leading=22)
    mini_title_style = ParagraphStyle('KoreanTitle', parent=styles['Normal'], fontName='NanumGothic-Bold', fontSize=15, leading=22)
    normal_style = ParagraphStyle('KoreanNormal', parent=styles['Normal'], fontName='NanumGothic', fontSize=12, leading=14)
    bold_style = ParagraphStyle('KoreanNormal', parent=styles['Normal'], fontName='NanumGothic-Bold', fontSize=12, leading=14)
    footer_style = ParagraphStyle('KoreanFooter', parent=styles['Normal'], fontName='NanumGothic', fontSize=9, alignment=TA_CENTER, textColor=colors.grey)


    # --- PDF 요소 구성 ---
    elements = []

    logo = Image("static/logo_low.png", width=45, height=40)
    text = Paragraph("전세가격지수 예측 보고서", title_style)
    empty = Paragraph("", normal_style)
    data = [[empty, text, logo]]
    table = Table(data, colWidths=[50, 420, 80])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    elements.append(table)

    elements += [
        HRFlowable(width="100%", thickness=2, color=colors.navy, spaceBefore=10, spaceAfter=10),
        Spacer(1, 12), 
        Paragraph("📊 1. 전세가격지수 예측", mini_title_style),
        Spacer(1, 12), 
        Paragraph("전세가격지수에 영향을 미치는 요인은 정책, 주택 매매 가격, 금리, 소비자물가지수, 유동성 및 주택담보대출 등이 있습니다.", bold_style),
        Spacer(1, 12),
        Paragraph("국토연구원에 따르면, 최근 전세가격 결정에 가장 큰 기여도를 보인 변수는 주택 매매가격과 양도성예금증서(CD) 금리로 나타났습니다. 매매가격이 상승하면 3~6개월 내에 전세가격도 상승하는 경향이 뚜렷하게 관찰되었습니다. 이외에도 공급 부족과 정부 정책(주택 공급 정책, 임대차 3법 등)이 전세가격에 영향을 미칩니다.", normal_style),
        
        Spacer(1, 12),
        HRFlowable(width="100%", thickness=1, color=colors.navy, spaceBefore=10, spaceAfter=10),
        Spacer(1, 12),
        Paragraph("본 예측 전세가격지수는 참고용으로만 사용해주세요.", normal_style),
        Spacer(1, 24),
        Paragraph("1-1. 전세가격지수 최근 15주 동향(표)", bold_style),
        Spacer(1, 12),
        Paragraph("선택 시점 기준 최근 15주에 대한 전세가격지수입니다.", normal_style),
        Paragraph("(기준시점 2025.03.31=100.0)", normal_style),
        Spacer(1, 12),
        Paragraph(f"지역1: {selected_region}", normal_style),
        Paragraph(f"지역2: {selected_region2}", normal_style),
        Paragraph(f"면적: {selected_label_kor}", normal_style),
        Spacer(1, 12),
    ]

    # 데이터 필터링
    filtered_df = filter_dataframe(df, selected_region, selected_region2, selected_label, selected_years)

    # 테이블 데이터 생성 및 추가
    table_data = [filtered_df.columns.tolist()] + filtered_df.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'NanumGothic-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(table)

    # 지역 정보 및 차트 이미지 추가
    elements += [
        Spacer(1, 12),
        PageBreak(),
        
        Spacer(1, 24),
        Paragraph("1-2. 전세가격지수 예측", bold_style),
        Spacer(1, 12),
        Paragraph(f"지역1: {selected_region}", normal_style),
        Paragraph(f"지역2: {selected_region2}", normal_style),
        Spacer(1, 24),
        build_chart_table(plot_urls, normal_style),
        Spacer(1, 105),
        PageBreak(),

        Spacer(1, 12),
        Paragraph("📈 2. 2025 부동산 시장 동향", mini_title_style),
        Spacer(1, 12),

        Paragraph("2025년 부동산 시장은 수도권과 지방 간의 가격 양극화가 더욱 뚜렷해질 전망입니다. 수도권은 매매 및 전세가격이 1~2% 내외로 완만하게 상승할 것으로 보이며, 지방은 매매가격이 보합세를 보이고, 전세가격은 약 2% 상승에 그칠 것으로 예상합니다. 전문가 90%가 서울 아파트값의 소폭 상승(1~5%)을 점치고 있으며, 지방은 보합 또는 하락을 전망하는 의견이 많습니다.", normal_style),
        Spacer(1, 12),
        Paragraph("2025년에는 한국은행의 기준금리 인하 기조가 이어지면서 대출금리 하락이 매수 심리를 자극할 수 있지만, 정부의 대출 규제와 거래량 감소가 가격 상승폭을 제한할 것으로 보입니다. 그러나 장기간의 고금리와 부동산 PF(프로젝트파이낸싱) 부실 문제로 인해 주택 공급이 부족한 상황이 지속되고 있습니다. 정부는 주택 공급 확대에 초점을 맞춘 정책을 추진중이나, 신축 입주물량 감소와 미분양 해소 지연이 가격 상승 압력으로 작용할 수 있습니다.", normal_style),
        Spacer(1, 12),
        Paragraph("서울 등 수도권은 신출 입주물량이 과거 평균 수준이나, 2026년부터 큰 폭으로 감소할 예정이어서 2025년부터 공급 부족에 따른 가격 상승 압력이 선반영될 가능성이 있습니다.", normal_style),
        
        Spacer(1, 15),
        Image('static/korea.png', width=500, height=150), 

        HRFlowable(width="100%", thickness=1, color=colors.navy, spaceBefore=10, spaceAfter=10),
        Spacer(1, 12),
        Paragraph("📈 3. 2025 전세 시장 동향", mini_title_style),
        Spacer(1, 12),

        Paragraph(" 2025년 전국 주택 전세가격에 대해 부동산전문가의 62%, 공인중개사의 61%가 상승할 것으로 전망하였습니다. 수도권은 부동산전문가(70%), 공인중개사(68%) 모두 전세가격 상승을 전망하였습니다.", normal_style),
        Spacer(1, 12),
        Paragraph(" 2025 KB 부동산 보고서에 따르면 올해 주택시장 7대 이슈로는 △주택시장 불안의 핵심 요인으로 지목되는 공급물량 △침체가 지속되고 있는 비수도권 주택시장 반등 가능성 △2025년 주택시장의 핵심 변수인 금리 인하와 대출 규제 △서민의 주된 주거 수단인 비아파트 시장 정상화 가능성 △우려와 기대 속에 본궤도에 오르는 노후계획도시 정비사업 △주택 경기 판단의 바로미터인 서울 아파트 시장 △상승세가 지속되고 있는 전세시장 불안 요인을 선정하였습니다.", normal_style),
        Spacer(1, 12),
        Paragraph(" 또한, 최근에는 전세보다 월세를 선호하는 경향이 강해지면서 전세 수요가 일부 감소하는 모습도 관찰됩니다. 전국적으로 2024년 대비 입주 물량이 약 40% 줄어들면서, 공급 부족에 따른 전세가격 상승 압력이 커지고 있습니다.", normal_style),
        Spacer(1, 36),
        
        Paragraph("본 보고서는 참고용 자료이며, 투자 결정의 근거가 될 수 없습니다.", footer_style),
        Paragraph("@ Copyrighted by Malhaebang", footer_style), 
    ]

    # --- PDF 생성 ---
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=50)
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="forecast_report.pdf", mimetype='application/pdf')

# 4. 오피스텔 전월세 가격 추이
@app.route('/chart', strict_slashes=False)
def chart():
    try:
        with open('static/office_monthly.json', 'r', encoding='utf-8') as f:
            office_monthly = json.load(f)
            # print("office_monthly loaded successfully") # 파일이 잘 로딩되었는지 로그로 확인
            # print(office_monthly)  

        with open('static/office_yearly.json', 'r', encoding='utf-8') as f:
            office_yearly = json.load(f)
            # print("office_yearly loaded successfully") # 파일이 잘 로딩되었는지 로그로 확인
            # print(office_yearly)  

        return render_template('chart.html', office_monthly=office_monthly, office_yearly=office_yearly)

    except Exception as e:
        print(f"Error loading JSON: {e}")
        return f"Error loading JSON file: {e}"

# pdf 페이지 상단 로고
def build_logo(logo_path):
    logo = Image(logo_path, width=50, height=40)
    logo_table = Table([[logo]], colWidths=[450])
    logo_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0)
    ]))
    return [logo_table, Spacer(1, 10)]

# 데이터프레임 필터링
def filter_dataframe(df, region1, region2, label, years):
    filtered = df[((df['지역'] == region1) | (df['지역'] == region2)) & (df['면적'].astype(str) == label)]
    if years:
        filtered = filtered.loc[:, filtered.columns[filtered.columns.str.contains('|'.join(years))]]
    filtered = filtered.T
    filtered.columns = [region1, region2]
    return filtered.tail(15)

# 데이터 테이블
def build_data_tables(df):
    data = [df.reset_index().columns.tolist()] + df.reset_index().values.tolist()
    
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ]))
    
    return [Spacer(1, 12), table, Spacer(1, 12)]

# 차트 테이블
def build_chart_table(base64_images, style):
    def decode_img(b64, w=300, h=240):
        return Image(BytesIO(base64.b64decode(b64)), width=w, height=h) if b64 else Paragraph(" ", style)

    rows = []

    if base64_images[0]:
        img = decode_img(base64_images[0], h=220)
        desc = Paragraph("선택하신 지역1에 대한 가격 동향입니다.", style)
        rows.append([img, desc])

    if base64_images[1]:
        img = decode_img(base64_images[1], h=220)
        desc = Paragraph("선택하신 지역1에 대한 3개월 예측치입니다.", style)
        rows.append([img, desc])

    if base64_images[2]:
        img = decode_img(base64_images[2], h=220)
        desc = Paragraph("선택하신 지역2에 대한 가격 동향입니다.", style)
        rows.append([img, desc])

    if base64_images[3]:
        img = decode_img(base64_images[3], h=220)
        desc = Paragraph("선택하신 지역2에 대한 3개월 예측치입니다.", style)
        rows.append([img, desc])

    table = Table(
        rows,
        colWidths=[350, 250],
        rowHeights=220
    )

    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    return table

# 페이지 넘버 & 상하단 라인 서식
def add_page_number(canvas, doc):
    width, height = A4
    canvas.setFont('NanumGothic', 9)

    # 상단라인
    canvas.setStrokeColor(colors.navy)
    canvas.setLineWidth(2)
    canvas.line(doc.leftMargin, height-30, width-doc.rightMargin, height-30)

    # 하단라인
    canvas.setStrokeColor(colors.navy)
    canvas.setLineWidth(2)
    canvas.line(doc.leftMargin, doc.bottomMargin-10, width-doc.rightMargin, doc.bottomMargin-10)

    # 페이지번호
    page_num = canvas.getPageNumber()
    text = f"{page_num}"
    canvas.saveState()
    canvas.drawCentredString(width / 2.0, doc.bottomMargin - 25, text)

    canvas.restoreState()


@app.route('/api/predict', methods=['POST'])
def predict_price():
    try:
        data = request.get_json()
        region = data.get('region')
        area = data.get('area')

        # 여기에 예측 로직 삽입
        prediction = 123.45
        confidence = 0.92

        return {
            "prediction": f"{prediction:.2f} 만원",
            "confidence": f"{confidence * 100:.1f}%"
        }

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
