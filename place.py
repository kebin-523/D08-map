import os

import requests
from dotenv import load_dotenv

load_dotenv(override=True)

# 🔌 API 주소는 여기 한 곳에만
API = {
    "keyword": "https://dapi.kakao.com/v2/local/search/keyword.json",  # 🔌 카카오 로컬 키워드로 장소 검색
}


def search_place(검색어, 개수=5):
    """검색어로 장소를 찾아 [{이름, 주소, 위도, 경도}, ...] 로 돌려준다.

    결과가 없으면 빈 리스트, 키·설정·연결 문제는 '⛔'로 시작하는 메시지의 RuntimeError.
    """
    키 = os.getenv("KAKAO_REST_API_KEY")
    if not 키:
        raise RuntimeError("⛔ .env에 KAKAO_REST_API_KEY가 없어요")

    try:
        res = requests.get(  # 🔌 API 호출
            API["keyword"],
            headers={"Authorization": f"KakaoAK {키}"},
            params={"query": 검색어, "size": 개수},
            timeout=10,
        )
    except requests.RequestException:
        raise RuntimeError("⛔ 카카오에 연결하지 못했어요. 인터넷을 확인해 주세요")

    if res.status_code == 401:
        raise RuntimeError("⛔ 카카오 REST API 키가 틀렸어요")
    if res.status_code == 403:
        raise RuntimeError("⛔ 카카오맵 사용 설정을 켜 주세요")
    if res.status_code != 200:
        raise RuntimeError(f"⛔ 카카오 응답 오류 (상태 코드 {res.status_code})")

    장소들 = []
    for d in res.json().get("documents", []):
        위도, 경도 = float(d["y"]), float(d["x"])  # 카카오: x=경도, y=위도
        if not (33 <= 위도 <= 39 and 124 <= 경도 <= 132):  # 한국 밖 좌표는 버림
            continue
        장소들.append(
            {
                "이름": d["place_name"],
                "주소": d.get("road_address_name") or d["address_name"],  # 도로명 없으면 지번
                "위도": 위도,
                "경도": 경도,
            }
        )
    return 장소들


if __name__ == "__main__":
    검색어 = input("검색어를 입력하세요 (예: 성수동 카페): ").strip()
    if not 검색어:
        print("검색어를 입력해 주세요")
    else:
        try:
            결과 = search_place(검색어)
        except RuntimeError as e:
            print(e)
        else:
            if not 결과:
                print(f"'{검색어}'을(를) 찾지 못했어요")
            for i, p in enumerate(결과, 1):
                print(f"{i}. {p['이름']} | {p['주소']} | ({p['위도']}, {p['경도']})")
    print("출처: 카카오 로컬 API (키워드로 장소 검색)")
