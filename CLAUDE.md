## 열쇠(키) 규칙
- 장소 검색·주소↔좌표는 파이썬에서 `os.getenv("KAKAO_REST_API_KEY")`로만 읽어 헤더 `Authorization: KakaoAK 키`로 호출.
- REST 키는 HTML·`map.html`·Streamlit 화면 어디에도 넣지 않는다.
- 지도 그리기에는 `KAKAO_JS_KEY`만 사용(`.env`에서 읽어 HTML 생성 시 삽입). 두 키는 서로 다른 값.
- 브라우저 `libraries=services`, 구글·네이버 지도 API는 쓰지 않는다. 표에 없는 API는 이름·주소·키 필요 여부를 말하고 확인받는다.
- `.env`는 만들거나 열어 보여 주지 않는다. 새 키 이름은 `.env.example`에만 추가(값은 사용자가 입력).
- 요청 주소·헤더·`response.url`·`res.text`를 출력하지 않는다.

## 좌표 규칙
- 카카오 응답 `x`=경도, `y`=위도(문자열). `float()`로 변환하고 `위도`·`경도`로 이름 붙인다.
- 지도 SDK는 `LatLng(위도, 경도)`, 요청 보낼 때는 `x=경도, y=위도`.
- 한국 밖 좌표(위도 33~39, 경도 124~132 밖)는 잘못된 값으로 보고 버린다.
- `road_address`는 null일 수 있음 → 없으면 지번 주소(`address`) 사용.

## 지도 HTML 규칙
- `map.html`은 파이썬이 생성. 실행 안내는 항상 `d8-map` 폴더에서 `python -m http.server 8000 --bind 127.0.0.1` → `http://localhost:8000/map.html`. file://(더블클릭) 안내 금지, `--bind 127.0.0.1` 절대 생략 금지.
- SDK: `https://dapi.kakao.com/v2/maps/sdk.js?appkey=JS키&autoload=false` + `kakao.maps.load(...)`.
- 지도 아래에 항상 안내 한 줄: "지도가 회색이면: ① 카카오맵 사용 설정 ② 지금 주소(포트까지) 등록 ③ 서버 주소로 열기".
- 장소 이름은 `textContent`, 데이터는 `json.dumps`로 삽입.
- 마커 여러 개면 `LatLngBounds`로 전부 보이게, 최대 200개.
- `map.html`은 `.gitignore`에 추가.

## Streamlit 규칙
- 실행: `streamlit run 파일.py`. 지도는 `st.iframe(html, height=...)` 사용, `st.components.v1.html` 금지.
- 안내에 카카오 콘솔 JavaScript SDK 도메인 `http://localhost:8501` 등록 필요 명시. `localhost:8502`·Network URL(IP)·`127.0.0.1`로 열면 안 뜬다고도 적는다.
- `load_dotenv(override=True)`. `.env` 수정 후 `Ctrl+C` → 다시 `streamlit run` 안내. 에러 결과는 캐시하지 않는다(캐시 함수 안에서 예외 → 밖에서 처리).
- 글자 설명은 `st.metric` 변화량 대신 `st.caption`.
- `requirements.txt`에 `streamlit>=1.66`.
- API 함수는 `@st.cache_data(ttl=600)`, 표·숫자는 `st.dataframe`/`st.metric`, 에러는 `st.error("한국어 한 줄")`.

## 판다스 규칙
- 동네 필터는 시·도까지 붙인 이름(`"서울특별시 강남구"`)으로.
- CSV는 `utf-8-sig` → `cp949` 순으로 읽고 사용한 인코딩을 출력.
- 읽은 직후 줄 수·칸 수·빈칸 개수(`shape`, `isna().sum()`)부터 보여 준다.
- 숫자 칸은 `pd.to_numeric(..., errors="coerce")`, "무료" 같은 글자는 먼저 0으로.
- 칸 이름은 파일에 실제 있는 것만 사용(모르면 `df.columns` 먼저 출력). 새 칸은 사용자가 요청할 때만 생성. `데이터기준일자`는 유지하고 기준일 표시.
- 빈 좌표를 카카오로 채울 때: 최대 30줄, 호출마다 `time.sleep(0.1)`, `⛔`로 시작하는 키·설정·연결 에러가 나면 즉시 중단.
- 저장은 `encoding="utf-8-sig"`, `index=False`. 원본 `*_raw.csv`는 `.gitignore`.
- 개수·평균은 코드로 계산하고, 엑셀 필터로 검산할 수 있게 조건을 출력.

## 공통 규칙 (D7과 동일)
- API 주소는 파일 맨 위 `API = {...}` 한 곳 + `# 🔌`, 요청 줄에 `# 🔌 API 호출`. `requests.get(..., timeout=10)`, 실패는 한국어 한 줄, 출력 맨 아래 출처.
- 새 패키지는 `requirements.txt`에 추가하고 설치 명령은 제안만. 커밋·푸시는 하지 말고 메시지만 제안, 커밋 전 `git status` 보여 주기.

## 쓸 수 있는 API
헤더는 모두 `Authorization: KakaoAK {REST API 키}`.

| 용도 | 주소 | 보내는 값 | 주요 칸 |
| --- | --- | --- | --- |
| 키워드 장소 검색 (+카테고리) | `https://dapi.kakao.com/v2/local/search/keyword.json` | `query`, 선택 `x`·`y`·`radius`(최대 20000m)·`sort=distance`·`category_group_code`·`size`(최대 15) | `place_name`, `road_address_name`, `address_name`, `x`, `y`, `phone`, `category_name`, `place_url`, `distance` |
| 카테고리 검색 (검색어 없이) | `https://dapi.kakao.com/v2/local/search/category.json` | `category_group_code`, `x`, `y`, `radius` | 위와 같음 |
| 주소→좌표 | `https://dapi.kakao.com/v2/local/search/address.json` | `query` | `documents[0].x`, `y`, `address_name` |
| 좌표→주소 | `https://dapi.kakao.com/v2/local/geo/coord2address.json` | `x`(경도), `y`(위도) | `road_address.address_name`(없을 수 있음), `address.address_name` |
| 지도 JS SDK | `https://dapi.kakao.com/v2/maps/sdk.js?appkey=JS키&autoload=false` | (브라우저) | `Map`, `LatLng(위도, 경도)`, `Marker`, `InfoWindow`, `LatLngBounds` |
| OpenWeather 현재 날씨 | D7 규칙 그대로 | `lat`, `lon`, `appid`, `units=metric`, `lang=kr` | `main.temp`, `weather[0].description` |

카테고리 코드: `CE7` 카페 · `FD6` 음식점 · `CS2` 편의점 · `PM9` 약국 · `HP8` 병원 · `SW8` 지하철역 · `PK6` 주차장 · `MT1` 대형마트 · `BK9` 은행 · `AT4` 관광명소 · `CT1` 문화시설

## 에러 안내
| 상황 | 뜻 | 화면 안내 |
| --- | --- | --- |
| 401 | REST 키 틀림(JS 키를 넣은 경우 많음) | "카카오 REST API 키가 틀렸어요" |
| 403 `disabled OPEN_MAP_AND_LOCAL service` | 카카오맵 사용 설정 OFF | "카카오맵 사용 설정을 켜 주세요" |
| `documents` 빈 목록 | 장소·주소 없음 | "'○○'을(를) 찾지 못했어요" |
| 지도가 회색/빈 화면 | JS 키·도메인·사용 설정·file:// 중 하나 | 지도 HTML의 안내 문장 |

## 실수에서 배운 규칙
<!-- AI 실수를 찾을 때마다 한 줄씩: - (날짜) (해라/하지 마라) ___ (왜: ___) → 검사: ___ -->
