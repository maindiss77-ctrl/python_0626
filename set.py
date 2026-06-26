# 중복이 가득한 리스트를 set으로 변환하면?
my_list = ["사과", "바나나", "사과", "포도", "바나나"]
my_set = set(my_list)

print(my_set)   
# 출력 결과: {'사과', '포도', '바나나'}  (중복이 사라짐!)


fruits = {"사과", "바나나"}

# 1. 새로운 요소 추가 (.add)
fruits.add("포도")
print(fruits)  # {'사과', '바나나', '포도'}

# 2. 기존 요소 삭제 (.remove)
fruits.remove("사과")
print(fruits)  # {'바나나', '포도'}