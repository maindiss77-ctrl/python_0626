# 리스트 컴프리헨션 문법 이해
# 1. 시작 데이터 선언
text = " 사과, 바나나 , , 포도 "
words = []

# 2. 문자열 치환 및 쪼개기 (replace & split)
# str(text)로 문자열 보장 후, 쉼표(,)를 공백(' ')으로 바꿉니다.
step1 = str(text).replace(',', ' ')

print(step1, type(step1))

# 공백을 기준으로 문자열을 잘라 리스트로 만듭니다.
# 파이썬의 .split()은 매개변수를 비워두면 연속된 여러 개의 공백을 알아서 하나로 취급
step2 = step1.split()
print(step2, type(step2))

# str(text).replace(',', ' ').split()가 가장 먼저 실행됩니다.
# for문 작동 (반복 시작)
# "오른쪽에서 재료(for)를 준비하고 
# ➔ 맨 오른쪽 필터(if)를 거쳐 
# ➔ 합격한 녀석들만 맨 앞(word.strip())에서 
# 예쁘게 포장되어 리스트로 완성된다!"

text2 ="파이썬 훈련에서 제일 중요한 것은, 문자열을 다루는 메서드 이해, 바로 그것이지"

words = [ word.strip() for word in str(text2).replace(',', ' ').split() if word.strip()]

print(words, type(words))