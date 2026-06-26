# region in word for region in all_region_names
# 실행 순서 (오른쪽 ➔ 왼쪽)



all_region_names = ["서울", "부산", "제주"]
# [1단계] 결과가 담길 빈 바구니 준비
result = []

# [2단계] 오른쪽의 for문이 먼저 실행됩니다.
for region in all_region_names:    
    # [3단계] 맨 앞에 있던 region(결과물)을 바구니에 담습니다.
    result.append(region)


word = """서울시청 주관으로 
지역 활성화를 위하여 잔치국수를 
시식하는 행사를 진행하였습니다. 
70세이상은 노인분들에게는 무료로 진행되며,
그외 노인분들은 단 돈 천원에
시식하실 수 있습니다.
거동이 불편하신 분들은 요양사들과 함께 참석이 가능합니다.
이날을 위해 준비한 행사는 그 밖에도 안마기계 체험도 있습니다.
협찬기업 바디프렌즈도 참석하여 함께 진행합니다.
70세 이하 60세 이상인 노인분들은 사회복지사와 참석하시면 무료로 시식하실 수 있습니다. 
"""
# 순서가 중요하지 않은 데이터
base_stop_words = {'노인', '참석', '일동', '주민', 
                   "지역", "마을", "노인들", "노인분들", "주민들","주민일동",
                   "이날" }
found_word = None
# 전체 문장이 실행되는 순서:
# 1) 오른쪽 컴프리헨션이 돌면서 하나씩 비교하고 ([True, False, False])
# 2) any()가 그걸 받아서 "True가 있네!" 하고 최종 True를 반환합니다.
if any(searchword in word for searchword in base_stop_words):
    print(f"위의 검수단어가 포함되어있습니다.")

findwords = []
for searchword in base_stop_words:
    if searchword in word:
        findwords.append(searchword) 

print(f"{findwords} 존재하는 단어만 수집")  


