# HR MVP

간단한 CSV 인사 명부를 기반으로 기본적인 통계와 검색 기능을 제공하는
바이브코딩형 MVP입니다. 개발지식이 없어도 Python 하나만 설치되어 있다면
터미널에서 바로 실행해볼 수 있도록 구성했습니다.

## 준비물

- Python 3.10 이상 (macOS, Windows, Linux 모두 가능)
- 터미널(명령 프롬프트)에서 `python` 명령을 실행할 수 있어야 합니다.

추가적인 라이브러리는 필요하지 않습니다. 저장소를 다운로드한 뒤 바로
실행하면 됩니다.

## 실행 방법

1. 터미널을 열고 이 저장소 폴더로 이동합니다.
   ```bash
   cd hr-mvp
   ```
2. 가장 쉬운 방법은 인터랙티브 메뉴를 여는 것입니다.
   ```bash
   python -m hr_mvp.cli
   ```
   번호를 선택하면 즉시 해당 기능이 실행됩니다. 언제든지 `Q`를 눌러 종료할 수 있습니다.
3. 특정 기능만 바로 실행하고 싶다면 다음과 같이 명령어를 사용할 수 있습니다.

   ### 1) 전체 요약 확인
   ```bash
   python -m hr_mvp.cli summary
   ```
   - 전체/재직 인원 수
   - 재직자의 평균 근속기간
   - 팀별 재직 인원, 재직구분별 인원 분포

   ### 2) 인원 목록 출력
   ```bash
   python -m hr_mvp.cli list
   ```
   `--active-only` 옵션을 추가하면 재직자만 표시합니다.

   ### 3) 이름·팀·직책으로 검색
   ```bash
   python -m hr_mvp.cli search --keyword GURM
   ```

   ### 4) 시용(수습) 종료 예정자 확인
   ```bash
   python -m hr_mvp.cli probation --within 60
   ```
   - `--within` 값으로 며칠 이내를 볼지 지정합니다. 기본은 30일입니다.
   - `--reference-date YYYY-MM-DD` 옵션을 주면 특정 기준일로 계산할 수 있습니다.

4. 다른 CSV 파일을 사용하고 싶다면 `--path` 옵션에 파일 경로를 지정하면 됩니다.
   ```bash
   python -m hr_mvp.cli summary --path 다른파일.csv
   ```

## 데이터 구조

`data/roster.csv` 파일에 아래와 같은 열이 포함되어 있습니다.

| 열 이름 | 설명 |
| --- | --- |
| employee_id | 사번 |
| payroll_id | 급여 사번 |
| name | 이름 |
| gender | 성별 |
| birthdate | 생년월일 (YYYY-MM-DD) |
| age_group | 연령대 |
| team | 팀 |
| part | 파트 |
| title | 직책 |
| start_date | 입사일 |
| probation_end | 시용 종료일 |
| resignation_date | 퇴사일 (없으면 공란) |
| tenure_text | 근속기간(문자열) |
| prior_experience_text | 입사 전 경력 (문자열) |
| total_experience_text | 총 경력 (문자열) |
| contract_type | 근로계약 형태 |
| phone | 개인 연락처 |
| email | 이메일 |
| work_location | 근무지 |
| job_type | 사무직/비사무직 구분 |
| employment_status | 재직 구분 |
| employment_status_detail | 재직 구분 상세 (현재 데이터에서는 공란) |
| prior_experience_months | 입사 전 경력(개월) |
| current_experience_months | 현 직장 경력(개월) |
| total_experience_months | 총 경력(개월) |

필요시 `data/roster.csv`를 엑셀에서 열어 그대로 수정한 뒤 저장하면 CLI에서도
바로 반영됩니다.

## 테스트

자동화 검증이 필요하다면 `pytest`로 간단한 테스트를 실행할 수 있습니다.
```bash
pytest
```

테스트는 기본 CSV가 정상적으로 로드되는지, 팀 통계와 검색 기능이 제대로
동작하는지 등을 확인합니다.
