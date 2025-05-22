from django.shortcuts import render
from .saju import make_saju, count_elements, recommend_house
import random
from .models import House
from django.views.decorators.clickjacking import xframe_options_exempt


def index(request):
    years = list(range(1950, 2025))
    months = list(range(1, 13))
    days = list(range(1, 32))

    return render(request, 'saju_app/index.html', {
        'years': years,
        'months': months,
        'days': days,
    })

# 조건에 맞는 추천 쿼리 (랜덤 5개)
def get_house_recommendations(preferred_direction):
    houses = House.objects.filter(direction__startswith=preferred_direction)
    return random.sample(list(houses), min(len(houses), 10))

# 결과 뷰 (사주 캐릭터 성향 추가)
@xframe_options_exempt
def result_view(request):
    if request.method == 'POST':
        try:

            birthdate = request.POST.get('birthdate')
            ampm = request.POST.get('ampm')
            hour = int(request.POST.get('hour'))
            minute = int(request.POST.get('minute'))

            year, month, day = map(int, birthdate.split('-'))

            if ampm == 'PM' and hour != 12:
                hour += 12
            elif ampm == 'AM' and hour == 12:
                hour = 0

        except Exception:
            return render(request, 'saju_app/result.html', {'error': '입력값 오류입니다.'})

        saju = make_saju(year, month, day, hour)
        elements = count_elements(saju)
        min_ele = min(elements, key=elements.get)
        recommendation = recommend_house(elements)

        ele_to_direction = {
            '화': '남향',
            '토': '남향',
            '수': '북향',
            '목': '동향',
            '금': '서향',
        }
        preferred_direction = ele_to_direction.get(min_ele, '남향')
        recommended_houses = get_house_recommendations(preferred_direction)

        # 오행별 성향 메시지
        character_traits = {
            "목": "🌱 푸른 새싹처럼 자라나는 당신, 무한한 꿈을 품고 창공을 향해 뻗어가는 목(木)의 기운을 지녔습니다.",
            "화": "🔥 불꽃처럼 타오르는 마음, 따스한 빛으로 어둠을 밝히는 화(火)의 열정을 품고 있지요.",
            "토": "⛰️ 굳건한 산처럼 묵묵히 세상을 지키는 당신, 든든한 뿌리로 삶의 터전을 단단히 다지는 토(土)의 기운을 품고 있습니다.",
            "금": "⚔️ 차가운 바람에 흔들리지 않는 칼날처럼, 단단한 의지와 결단력으로 세상을 가르는 금(金)의 기운을 지녔습니다.",
            "수": "💧 깊은 호수처럼 고요하고 넓은 마음, 흐르는 물처럼 지혜와 감성을 담아내는 수(水)의 기운을 품고 있습니다.",
        }


        # 오행 중 가장 많은 요소 선택 (기본 성향 판단용)
        max_ele = max(elements, key=elements.get)
        character_message = character_traits.get(max_ele, "당신의 성향을 분석 중입니다.")

        context = {
            'saju': saju,
            'elements': elements,
            'recommendation': recommendation,
            'recommended_houses': recommended_houses,
            'preferred_direction': preferred_direction,
            'character_message': character_message,
        }

        return render(request, 'saju_app/result.html', context)

    return render(request, 'saju_app/index.html')

