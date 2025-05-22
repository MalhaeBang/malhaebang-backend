from datetime import date
from lunardate import LunarDate

HEAVENLY_STEMS = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
EARTHLY_BRANCHES = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']

HEAVENLY_STEMS_ELE = {
    '갑': '목', '을': '목',
    '병': '화', '정': '화',
    '무': '토', '기': '토',
    '경': '금', '신': '금',
    '임': '수', '계': '수',
}

EARTHLY_BRANCHES_ELE = {
    '인': '목', '묘': '목',
    '사': '화', '오': '화',
    '축': '토', '진': '토', '미': '토', '술': '토',
    '신': '금', '유': '금',
    '자': '수', '해': '수',
}

def get_ganji(year):
    # 년간/년지 계산 (근사치)
    year_gan = HEAVENLY_STEMS[(year - 4) % 10]
    year_ji = EARTHLY_BRANCHES[(year - 4) % 12]
    return year_gan, year_ji

def get_month_branch_by_solar_date(month, day):
    # 월지 시작일을 절기 기준으로 간단히 보정 (근사치, 정확 X)
    solar_term_start = [
        (2, 4),  # 인월 시작 (입춘)
        (3, 6),  # 묘월 시작 (경칩)
        (4, 5),  # 진월 (청명)
        (5, 6),  # 사월 (입하)
        (6, 6),  # 오월 (망종)
        (7, 7),  # 미월 (소서)
        (8, 8),  # 신월 (입추)
        (9, 8),  # 유월 (백로)
        (10, 8), # 술월 (한로)
        (11, 7), # 해월 (입동)
        (12, 7), # 자월 (대설)
        (1, 6),  # 축월 (소한)
    ]
    
    # 실제 월지 번호는 인(0)부터 시작
    for i, (m, d) in enumerate(solar_term_start):
        if (month, day) < (m, d):
            return (i - 1) % 12
    return 11  # 1월 6일 이후는 축월

def get_month_ganji_fixed(year_gan_index, month, day):
    branch_index = get_month_branch_by_solar_date(month, day)
    # 월간은 (년간 인덱스 * 2 + 월지 인덱스) % 10
    gan_index = (year_gan_index * 2 + branch_index) % 10
    return HEAVENLY_STEMS[gan_index], EARTHLY_BRANCHES[(branch_index + 2) % 12]


def get_day_ganji(year, month, day):
    # 양력 날짜 -> 음력 날짜 변환
    try:
        lunar_date = LunarDate.fromSolarDate(year, month, day)
    except Exception as e:
        print("음력 변환 실패:", e)
        return None, None

    # 기준일: 1984-02-02 (갑자일) - 60갑자 주기 시작점
    base = date(1984, 2, 2)
    target = date(year, month, day)

    diff = (target - base).days
    if diff < 0:
        diff = diff % 60

    gan_index = diff % 10
    ji_index = diff % 12

    return HEAVENLY_STEMS[gan_index], EARTHLY_BRANCHES[ji_index]

def get_hour_ji(hour):
    # 시지는 2시간 단위로 12지지 적용
    index = ((hour + 1) // 2) % 12
    return EARTHLY_BRANCHES[index]

def make_saju(year, month, day, hour):
    year_gan, year_ji = get_ganji(year)
    year_gan_index = (year - 4) % 10

    month_gan, month_ji = get_month_ganji_fixed(year_gan_index, month, day)
    day_gan, day_ji = get_day_ganji(year, month, day)
    hour_ji = get_hour_ji(hour)

    return {
        'year': (year_gan, year_ji),
        'month': (month_gan, month_ji),
        'day': (day_gan, day_ji),
        'hour': hour_ji,
    }


def count_elements(saju):
    counts = {'목':0, '화':0, '토':0, '금':0, '수':0}

    # 년간/년지
    yg, yj = saju['year']
    counts[HEAVENLY_STEMS_ELE[yg]] += 1
    counts[EARTHLY_BRANCHES_ELE[yj]] += 1

    # 월간/월지
    mg, mj = saju['month']
    counts[HEAVENLY_STEMS_ELE[mg]] += 1
    counts[EARTHLY_BRANCHES_ELE[mj]] += 1

    # 일간/일지
    dg, dj = saju['day']
    counts[HEAVENLY_STEMS_ELE[dg]] += 1
    counts[EARTHLY_BRANCHES_ELE[dj]] += 1

    # 시지
    hj = saju['hour']
    counts[EARTHLY_BRANCHES_ELE[hj]] += 1

    return counts

def recommend_house(element_counts):
    # 단순 추천 로직: 가장 적은 오행에 따른 집 추천
    min_ele = min(element_counts, key=element_counts.get)
    if min_ele == '화':
        return "☀️ 남향집 (따뜻하고 밝은 환경 추천)"
    elif min_ele == '토':
        return "🌄 남향/동향집 (안정적이고 편안한 환경 추천)"
    elif min_ele == '수':
        return "💧 북향집 (물가 근처 추천)"
    elif min_ele == '목':
        return "🌳 동향집 (녹지 공간이 많은 집 추천)"
    elif min_ele == '금':
        return "🏙️ 서향집 (깔끔하고 현대적인 집 추천)"
    else:
        return "🏠 기본적인 집 추천"


