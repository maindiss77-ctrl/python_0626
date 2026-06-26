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

# 3. 그래프 도화지 생성
plt.figure(figsize=(14, 7))

# 4. 막대바 생성 (X축: 상세지역, Y축: 뉴스건수)
# 범례(hue)에 '상위3개키워드'를 매핑하여 막대마다 어떤 키워드가 핵심인지 노출합니다.
ax = sns.barplot(
    data=visual_df.reset_index(), 
    x='상세지역', 
    y='뉴스건수', 
    hue='상위3개키워드', 
    dodge=False,       # 지역별로 하나의 막대만 깔끔하게 노출되도록 설정
    palette='viridis'   # 직관적이고 세련된 컬러 맵 적용
)

# 5. 그래프 세부 디자인 및 레이블 설정
plt.title('지역 뉴스에 나타난 핵심 지역 분포 및 Top 3 키워드', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('상세 지역 (대분류 > 소분류 정제)', fontsize=12, labelpad=10)
plt.ylabel('뉴스 빈도수 (건)', fontsize=12, labelpad=10)
plt.xticks(rotation=45) # 지역명이 겹치지 않도록 45도 회전
plt.grid(axis='y', linestyle='--', alpha=0.7) # 가로 점선 추가로 가독성 향상

# 6. 각 막대 위에 뉴스 건수 수치 표시 (텍스트 라벨링)
for p in ax.patches:
    if p.get_height() > 0: # 0건 이상인 경우만 표시
        ax.annotate(
            f"{int(p.get_height()):,}", 
            (p.get_x() + p.get_width() / 2., p.get_height()), 
            ha='center', va='center', 
            xytext=(0, 8), 
            textcoords='offset points', 
            fontsize=10, fontweight='bold'
        )

# 7. 범례(Legend) 위치 및 스타일 세부 조정
# 그래프 우측 바깥에 깔끔하게 배치하여 그래프 영역을 침범하지 않도록 함
plt.legend(
    title="지역별 핵심 키워드 (Top 3)", 
    bbox_to_anchor=(1.05, 1), 
    loc='upper left', 
    fontsize=10, 
    title_fontsize=11
)

# 8. 레이아웃 자동 조정 및 출력
plt.tight_layout()
plt.show()



