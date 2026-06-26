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
# [시각화 구현] 지역별 3개 막대 그래프 출력
# --------------------------------------------------
plt.figure(figsize=(15, 8))


ax = sns.barplot(
    data=visual_df,
    x='상세지역',
    y='뉴스건수',
    hue='키워드',
    palette='tab20' # 다양한 키워드를 구분하기 위해 색상 스펙트럼이 넓은 팔레트 사용
)

# 그래프 기본 디자인
plt.title('상세지역별 상위 핵심 키워드(Top 3) 빈도수 분포', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('상세 지역', fontsize=12, labelpad=10)
plt.ylabel('뉴스 빈도수 (건)', fontsize=12, labelpad=10)
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.5)

# 각 막대 위에 정확한 뉴스 건수 수치 표시
for p in ax.patches:
    if p.get_height() > 0:
        ax.annotate(
            f"{int(p.get_height()):,}", 
            (p.get_x() + p.get_width() / 2., p.get_height()), 
            ha='center', va='center', 
            xytext=(0, 5), 
            textcoords='offset points', 
            fontsize=9
        )

# 범례(Legend) 설정 - 키워드가 많으므로 우측 레이아웃 밖으로 완전히 뺍니다.
plt.legend(
    title="핵심 키워드", 
    bbox_to_anchor=(1.02, 1), 
    loc='upper left', 
    fontsize=10, 
    title_fontsize=11
)

plt.tight_layout()
plt.show()



