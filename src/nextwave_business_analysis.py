
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
xl = pd.ExcelFile('data.xlsx')

df_funnel = xl.parse('DS1_funnel_summary')
df_channel = xl.parse('DS2_channel_performance')
df_landing = xl.parse('DS3_landing_event_log')
df_trial = xl.parse('DS4_trial_usage_summary')
df_retention = xl.parse('DS5_segment_retention')
df_feedback = xl.parse('DS6_customer_feedback_summary')

print("로드 완료")


df_funnel = xl.parse('DS1_funnel_summary', header=1)
df_funnel.columns = ['month', '방문 유저 수', '회원가입 유저', '무료 체험 유저', '유료 결제 유저', '한달 유지']

df_channel = xl.parse('DS2_channel_performance', header=1)
df_channel.columns = ['month', '유입 채널', '방문자 수', '회원가입 전환율', '무료체험 시작률', '유료 전환율']

df_landing = xl.parse('DS3_landing_event_log', header=1)
df_landing.columns = ['단계', '사용자 수', '이탈률']

df_trial = xl.parse('DS4_trial_usage_summary', header=1)
df_trial.columns = ['기능', '기능 사용자 수', '평균 사용 횟수', '유료 전환율']

df_retention = xl.parse('DS5_segment_retention', header=1)
df_retention.columns = ['고객 유형', '4주차 유지율']

df_feedback = xl.parse('DS6_customer_feedback_summary', header=1)
df_feedback.columns = ['이슈 유형', '비중']


# 01. EDA 검증
# 월별 KPI 전환율 추이
# 전환율 계산
df_funnel['회원가입 전환율'] = df_funnel['회원가입 유저'] / df_funnel['방문 유저 수'] * 100
df_funnel['무료체험 시작률'] = df_funnel['무료 체험 유저'] / df_funnel['방문 유저 수'] * 100
df_funnel['유료 전환율'] = df_funnel['유료 결제 유저'] / df_funnel['방문 유저 수'] * 100
df_funnel['4주차 유지율'] = df_funnel['한달 유지'] / df_funnel['방문 유저 수'] * 100

# 그래프
fig, ax = plt.subplots(figsize=(10, 5))

for col in ['회원가입 전환율', '무료체험 시작률', '유료 전환율', '4주차 유지율']:
    ax.plot(df_funnel['month'], df_funnel[col], marker='o', label=col)

ax.set_title('월별 KPI 전환율 추이', fontsize=14)
ax.set_xlabel('월')
ax.set_ylabel('전환율 (%)')
ax.legend()
ax.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('eda_kpi_trend.png', dpi=150)
plt.show()
print("로드 완료")

# 퍼널 단계별 사용자 수
fig, ax = plt.subplots(figsize=(10, 5))

ax.bar(df_landing['단계'], df_landing['사용자 수'], color='steelblue')
ax.set_title('퍼널 단계별 사용자 수 (4월)', fontsize=14)
ax.set_xlabel('단계')
ax.set_ylabel('사용자 수')
ax.grid(True, axis='y', linestyle='--', alpha=0.5)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig('eda_funnel.png', dpi=150)
plt.show()



# 02. 세부 가설 1 검증 - "가입할 이유를 못 느껴서 CTA를 안 누른다"
# CTA 클릭률 vs 이후 단계 이탈률 비교
stages = df_landing['단계']
users = df_landing['사용자 수']

# 단계별 이탈률 계산
dropout = []
for i in range(len(users)-1):
    rate = (users.iloc[i] - users.iloc[i+1]) / users.iloc[i] * 100
    dropout.append(round(rate, 1))
dropout.append(0)

df_landing['실제 이탈률'] = dropout

# 그래프
fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.bar(stages, users, color='steelblue', alpha=0.6, label='사용자 수')
ax1.set_ylabel('사용자 수')

ax2 = ax1.twinx()
ax2.plot(stages, df_landing['실제 이탈률'], color='red', marker='o', label='이탈률(%)')
ax2.set_ylabel('이탈률 (%)')

ax1.set_title('퍼널 단계별 사용자 수 및 이탈률', fontsize=14)
plt.xticks(rotation=15)
fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))
plt.tight_layout()
plt.savefig('hypothesis1.png', dpi=150)
plt.show()


# 03. 세부가설 2 검증 - "핵심 기능을 못 찾고 떠난다"

fig, ax1 = plt.subplots(figsize=(10, 5))

# 기능별 사용자 수 막대
ax1.bar(df_trial['기능'], df_trial['기능 사용자 수'], color='steelblue', alpha=0.6, label='사용자 수')
ax1.set_ylabel('사용자 수')

# 유료 전환율 꺾은선
ax2 = ax1.twinx()

# 퍼센트 문자열을 숫자로 변환
df_trial['유료 전환율 수치'] = df_trial['유료 전환율']
ax2.plot(df_trial['기능'], df_trial['유료 전환율 수치'], color='red', marker='o', label='유료 전환율(%)')
ax2.set_ylabel('유료 전환율 (%)')

ax1.set_title('기능별 사용자 수 vs 유료 전환율', fontsize=14)
fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))
plt.tight_layout()
plt.savefig('hypothesis2.png', dpi=150)
plt.show()


# 04. 세부 가설 3 검증 - "SNS가 트래픽을 희석시킨다"

fig, ax1 = plt.subplots(figsize=(10, 5))

# 채널별 방문자 수 막대
ax1.bar(df_channel['유입 채널'], df_channel['방문자 수'], color='steelblue', alpha=0.6, label='방문자 수')
ax1.set_ylabel('방문자 수')

# 유료 전환율 꺾은선
ax2 = ax1.twinx()
ax2.plot(df_channel['유입 채널'], df_channel['유료 전환율'], color='red', marker='o', label='유료 전환율(%)')
ax2.set_ylabel('유료 전환율 (%)')


ax1.set_title('채널별 방문자 수 vs 유료 전환율', fontsize=14)
fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))
plt.tight_layout()
plt.savefig('hypothesis3.png', dpi=150)
plt.show()


# 05. 개선 우선순위 계산
# 4월 기준 현재 수치
visitors = 56000
cta_click_rate = 14560 / 56000        # CTA 클릭률
email_complete_rate = 4830 / 9920     # 이메일 인증 완료율
signup_complete_rate = 3528 / 4830    # 가입 완료율
trial_rate = 1623 / 3528              # 무료체험 시작률
paid_rate = 584 / 1623                # 유료 전환율

# 현재 유료결제 유저
current_paid = visitors * cta_click_rate * email_complete_rate * signup_complete_rate * trial_rate * paid_rate
print(f"현재 유료결제 유저: {round(current_paid)}명")

# 시나리오 1: CTA 클릭률 개선 (74% 이탈 → 60% 이탈)
new_cta = 56000 * 0.40  # 40% 클릭
scenario1 = new_cta * email_complete_rate * signup_complete_rate * trial_rate * paid_rate
print(f"시나리오1 (랜딩 개선): {round(scenario1)}명 (+{round(scenario1 - current_paid)}명)")

# 시나리오 2: 핵심 기능 노출 확대 (알림자동화 사용자 비중 증가)
# 현재 평균 전환율
current_trial_paid_rate = 584 / 1623
# 알림자동화 비중 10% 증가 시 가중 전환율
new_trial_paid_rate = current_trial_paid_rate * 0.9 + 0.41 * 0.1
scenario2 = visitors * cta_click_rate * email_complete_rate * signup_complete_rate * trial_rate * new_trial_paid_rate
print(f"시나리오2 (기능 노출 개선): {round(scenario2)}명 (+{round(scenario2 - current_paid)}명)")

# 시나리오 3: SNS 비중 축소 (31% → 15%), 지인추천 확대
current_avg_rate = df_channel['유료 전환율'].mean()
new_avg_rate = (0.15 * 0.007 + 0.32 * 0.018 + 0.20 * 0.022 + 0.33 * 0.028)
scenario3_visitors = visitors * (new_avg_rate / current_avg_rate) * visitors / visitors
scenario3 = visitors * cta_click_rate * email_complete_rate * signup_complete_rate * trial_rate * (new_avg_rate / current_avg_rate * paid_rate)
print(f"시나리오3 (채널 믹스 개선): {round(scenario3)}명 (+{round(scenario3 - current_paid)}명)")


# 개선 우선순위 시각화
labels = ['랜딩페이지 개선', '채널 믹스 조정', '핵심 기능 노출 확대']
increases = [462, 78, 12]
colors = ['#2F4F8F', '#5B7DB1', '#A8BFDD']

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(labels, increases, color=colors)

# 막대 위에 숫자 표시
for bar, val in zip(bars, increases):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f'+{val}명', ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_title('개선 포인트별 유료결제 증가 예상 인원', fontsize=14)
ax.set_ylabel('유료결제 증가 인원 (명)')
ax.set_ylim(0, 550)
ax.grid(True, axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('priority.png', dpi=150)
plt.show()

