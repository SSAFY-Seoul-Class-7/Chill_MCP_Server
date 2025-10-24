# 🏆 ChillMCP 공식 검증 테스트

해커톤 공식 검증 기준에 따른 종합 테스트 모음입니다.

## 📁 파일 구조

```
tests/official_validation/
├── base_validator.py              # 공통 기능을 위한 베이스 클래스
├── test_1_command_line_parameters.py  # 테스트 1: 커맨드라인 파라미터 (필수)
├── test_2_continuous_break.py     # 테스트 2: 연속 휴식 테스트
├── test_3_stress_accumulation.py  # 테스트 3: 스트레스 누적 테스트
├── test_4_delay_when_boss_alert_5.py  # 테스트 4: Boss Alert Level 5 지연 테스트
├── test_5_response_parsing.py     # 테스트 5: 응답 파싱 테스트
├── test_6_cooldown.py            # 테스트 6: Cooldown 테스트
├── run_all_tests.py              # 모든 테스트 실행
└── README.md                     # 이 파일
```

## 🚀 사용 방법

### 모든 테스트 실행

```bash
cd tests/official_validation
python run_all_tests.py
```

### 개별 테스트 실행

```bash
cd tests/official_validation

# 테스트 1: 커맨드라인 파라미터 (필수)
python test_1_command_line_parameters.py

# 테스트 2: 연속 휴식
python test_2_continuous_break.py

# 테스트 3: 스트레스 누적
python test_3_stress_accumulation.py

# 테스트 4: Boss Alert Level 5 지연
python test_4_delay_when_boss_alert_5.py

# 테스트 5: 응답 파싱
python test_5_response_parsing.py

# 테스트 6: Cooldown
python test_6_cooldown.py
```

## 📋 테스트 시나리오

### 테스트 1: 커맨드라인 파라미터 (필수 - 미통과 시 실격)

- `--boss_alertness` 파라미터 인식 및 정상 동작
- `--boss_alertness_cooldown` 파라미터 인식 및 정상 동작
- 파라미터 미지원 시 자동 검증 실패 처리

### 테스트 2: 연속 휴식 테스트

- 여러 도구를 연속으로 호출하여 Boss Alert Level 상승 확인
- `boss_alertness=100`일 때 Boss Alert Level이 상승하는지 검증

### 테스트 3: 스트레스 누적 테스트

- 시간 경과에 따른 Stress Level 자동 증가 확인
- 1분에 1포인트씩 상승하는 메커니즘 검증

### 테스트 4: Boss Alert Level 5 지연 테스트

- Boss Alert Level 5일 때 20초 지연 동작 확인
- 19~22초 범위 내에서 지연이 발생하는지 검증

### 테스트 5: 응답 파싱 테스트

- 표준 MCP 응답 구조 준수
- 파싱 가능한 텍스트 형식 출력
- Break Summary, Stress Level, Boss Alert Level 필드 포함
- 정규표현식으로 정확한 값 추출 가능성 확인

### 테스트 6: Cooldown 테스트

- `--boss_alertness_cooldown` 파라미터에 따른 Boss Alert Level 감소 확인
- 지정된 주기마다 1포인트씩 감소하는 메커니즘 검증

## 🔍 정규표현식 검증

해커톤 요구사항에 맞는 정규표현식 패턴:

```python
# Break Summary 추출
break_summary_pattern = r"Break Summary:\s*(.+?)(?:\n|$)"

# Stress Level 추출 (0-100 범위)
stress_level_pattern = r"Stress Level:\s*(\d{1,3})"

# Boss Alert Level 추출 (0-5 범위)
boss_alert_pattern = r"Boss Alert Level:\s*([0-5])"
```

## ⚠️ 중요 사항

1. **테스트 1은 필수**입니다. 이 테스트를 통과하지 못하면 즉시 실격 처리됩니다.
2. 모든 테스트는 서버를 시작하고 종료하는 과정을 포함합니다.
3. 테스트 간 충돌을 방지하기 위해 각 테스트 후 서버를 정리합니다.
4. 정규표현식 검증은 해커톤 요구사항과 정확히 일치합니다.

## 🎯 해커톤 검증 기준 준수

- ✅ 커맨드라인 파라미터 지원 (필수)
- ✅ MCP 서버 기본 동작
- ✅ 상태 관리 검증
- ✅ 응답 형식 검증
- ✅ 모든 필수 테스트 시나리오 포함
