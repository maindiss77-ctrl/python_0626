# [상세지역, 키워드] 쌍으로 완전히 쪼개어 빈도수를 계산하는 시각화

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from collections import Counter

file_path = './원본/한국언론진흥재단_뉴스빅데이터_메타데이터_노인_20011231.csv' 
df = pd.read_csv(file_path, encoding='cp949')

plt.rcParams["font.family"] = "Malgun Gothic"  
plt.rcParams["axes.unicode_minus"] = False  

base_stop_words = {'노인', '참석', '일동', '주민', 
                   "지역", "마을", "노인들", "노인분들", "주민들","주민일동",
                   "이날" }

region_mask = df["통합 분류1"].notna() & df["통합 분류1"].str.contains("지역")
df_region = df[region_mask].copy() 

df_region['상세지역'] = df_region['통합 분류1'].apply(
    lambda x: x.split('-')[-1].strip() if '-' in str(x) else x.strip()
)

df_region['키워드'] = df_region['키워드'].fillna('')
# 빈문자열이라도 삽입
all_region_names = list(df_region['상세지역'].dropna().unique())


def get_top_10_keywords(series):   
    all_text = " ".join(series.astype(str))    
    words = [word.strip() for word in all_text.replace(',', ' ').split() if word.strip()]
    top_10 = [item[0] for item in Counter(words).most_common(5)]
    return top_10

def get_clean_keywords(text):
    if not text: return []
    words = [word.strip() for word in str(text).replace(',', ' ').split() if word.strip()]    
    clean_words = []
    for word in words:
        if word in base_stop_words: continue
        if any(region in word for region in all_region_names): continue
        clean_words.append(word)
    return clean_words

def merge_and_rank(series):
    merged_list = [word for sublist in series for word in sublist]
    return [item[0] for item in Counter(merged_list).most_common(10)]


df_region['정제된_리스트'] = df_region['키워드'].apply(get_clean_keywords)



# 시각화용 데이터셋 재정비 (뉴스 건수 계산 및 키워드 3위 슬라이싱)
# groupby 과정에서 뉴스건수를 함께 구합니다.
visual_df = df_region.groupby('상세지역').agg(
    뉴스건수=('상세지역', 'count'),
    키워드순=('정제된_리스트', merge_and_rank)
).sort_values(by='뉴스건수', ascending=False) # 뉴스 건수 많은 순 정렬

# 범례에 표시할 '상위 3개 키워드' 문자열 가공 (예: "복지, 일자리, 건강")
visual_df['상위3개키워드'] = visual_df['키워드순'].apply(lambda x: ', '.join(x[:3]))


exploded_records = []

for idx, row in df_region.iterrows():
    region = row['상세지역']
    # 이미 불용어와 지역명이 제거된 '정제된_리스트'를 사용합니다.
    clean_words = row['정제된_리스트'] 
    
    for word in clean_words:
        exploded_records.append({'상세지역': region, '키워드': word})

# 개별 키워드 단위의 새로운 데이터프레임 생성
df_words = pd.DataFrame(exploded_records)

# 지역별로 각 키워드가 몇 번씩 등장했는지 빈도수 집계
df_word_counts = df_words.groupby(['상세지역', '키워드']).size().reset_index(name='뉴스건수')

# 각 지역 내에서 빈도수 순으로 순위를 매겨 상위 3개 키워드만 필터링
df_word_counts['순위'] = df_word_counts.groupby('상세지역')['뉴스건수'].rank(method='first', ascending=False)
visual_df = df_word_counts[df_word_counts['순위'] <= 3].copy()

# 보기 좋게 뉴스 건수가 많은 상세지역 순서대로 정렬
region_order = visual_df.groupby('상세지역')['뉴스건수'].sum().sort_values(ascending=False).index
visual_df['상세지역'] = pd.Categorical(visual_df['상세지역'], categories=region_order, ordered=True)
visual_df = visual_df.sort_values('상세지역')


# --------------------------------------------------
# [시각화 구현] 너비를 넓히고 틈새를 없앤 그룹 막대 그래프
"""Seaborn의 barplot에서 hue를 사용할 때, 특정 지역(예: '경북', '전남')에 
모든 키워드가 공통으로 존재하지 않으면 비어 있는 
키워드의 자리를 공백(자리 빼기)으로 남겨두기 때문에 
막대가 얇아지고 서로 멀리 떨어지는 현상이 발생
"""
# --------------------------------------------------
# [데이터 정렬 및 위치 계산] 여백 없는 밀착형 막대 배치
# --------------------------------------------------
# X축에 나열할 상세지역 순서 (기존 방식 유지)
regions = visual_df['상세지역'].unique()

plt.figure(figsize=(15, 8))

# 하나의 지역 영역에 할당할 총 너비 (1.0이면 지역 간 빈틈이 아예 없어짐)
total_width = 0.8  
# 각 지역당 막대가 3개씩 들어가므로, 개별 막대의 너비는 총 너비를 3등분한 값
bar_width = total_width / 3  

# 색상 팔레트 설정 (키워드가 매번 바뀌므로 고유한 색상 추출용)
colors = plt.colormaps['tab20'].colors

# 전역 키워드-색상 매핑 사전 (범례용)
unique_keywords = visual_df['키워드'].unique()
keyword_color_map = {kw: colors[i % len(colors)] for i, kw in enumerate(unique_keywords)}

# --------------------------------------------------
# [루프 돌며 막대 그리기] 빈자리 없이 강제로 밀착
# --------------------------------------------------
# 범례 중복 표시를 방지하기 위한 집합
rendered_keywords = set()

for i, region in enumerate(regions):
    # 해당 지역의 데이터만 필터링 (최대 3개 행)
    region_data = visual_df[visual_df['상세지역'] == region].sort_values(by='뉴스건수', ascending=False)
    
    # 💥 핵심 포인트: 데이터가 3개보다 적더라도 빈 자리를 두지 않고 있는 만큼만 밀착해서 그리기
    for j, (_, row) in enumerate(region_data.iterrows()):
        kw = row['키워드']
        val = row['뉴스건수']
        
        # j번째 막대의 정확한 X축 중심 위치 계산 (중앙 정렬)
        # 3개일 때 기준: j=0(왼쪽), j=1(중앙), j=2(오른쪽)로 빈틈없이 정렬됨
        x_pos = i + (j - (len(region_data) - 1) / 2) * bar_width
        
        # 범례 레이블은 최초 1번만 등록되도록 설정
        label = kw if kw not in rendered_keywords else ""
        if label:
            rendered_keywords.add(kw)
            
        # 막대 출력 (gap이 없으므로 두껍고 완벽하게 밀착됨)
        rect = plt.bar(
            x_pos, val, 
            width=bar_width, 
            color=keyword_color_map[kw], 
            edgecolor='none',  # 막대 테두리 선 제거로 밀착감 극대화
            label=label
        )
        
        # 막대 위 수치 라벨링
        plt.annotate(
            f"{int(val):,}",
            xy=(x_pos, val),
            xytext=(0, 5),
            textcoords='offset points',
            ha='center', va='bottom',
            fontsize=9, fontweight='bold'
        )

# --------------------------------------------------
# 그래프 레이아웃 스타일링
# --------------------------------------------------
plt.title('상세지역별 상위 핵심 키워드(Top 3) 빈도수 분포', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('상세 지역', fontsize=12, labelpad=10)
plt.ylabel('뉴스 빈도수 (건)', fontsize=12, labelpad=10)

# X축 눈금을 각 지역의 중앙에 배치
plt.xticks(range(len(regions)), regions, rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.3)

# 범례 깔끔하게 우측 바깥으로 정리
plt.legend(
    title="핵심 키워드", 
    bbox_to_anchor=(1.02, 1), 
    loc='upper left', 
    fontsize=10, 
    title_fontsize=11
)

plt.tight_layout()
plt.show()
