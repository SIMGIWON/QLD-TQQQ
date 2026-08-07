"""
price_data.json 을 최신 QQQ/QLD/TQQQ 종가로 갱신하는 스크립트.
- 기존에 저장된 날짜는 절대 건드리지 않고, price_data.json의 마지막 날짜 다음날부터
  오늘까지 새로 발표된 종가만 뒤에 이어붙입니다.
- GitHub Actions에서 매일 실행되도록 설계했지만, 로컬에서 `python update_price_data.py`
  로 수동 실행해도 동일하게 동작합니다.
"""

import json
import sys
from datetime import date, timedelta

import yfinance as yf

PRICE_FILE = "price_data.json"
TICKERS = {"p1": "QQQ", "p2": "QLD", "p3": "TQQQ"}


def load_price_data():
    with open(PRICE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_price_data(data):
    with open(PRICE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))


def main():
    data = load_price_data()
    last_date = data["dates"][-1]
    print(f"기존 마지막 날짜: {last_date} (총 {len(data['dates'])}일)")

    start = date.fromisoformat(last_date) + timedelta(days=1)
    end = date.today() + timedelta(days=1)  # yfinance의 end는 미포함이라 하루 더 줌

    if start >= end:
        print("이미 최신 상태입니다. 갱신할 데이터가 없어요.")
        return

    # 세 종목을 한번에 다운로드 (종가만 사용)
    raw = yf.download(
        list(TICKERS.values()),
        start=start.isoformat(),
        end=end.isoformat(),
        interval="1d",
        auto_adjust=False,
        progress=False,
    )

    if raw.empty:
        print("새로 발표된 거래일 데이터가 없습니다 (주말/휴장일일 수 있음).")
        return

    close = raw["Close"]

    # 세 종목 모두 값이 있는 날짜만 사용 (하나라도 결측이면 그날은 스킵 -> 다음 실행에서 재시도)
    valid = close.dropna(subset=list(TICKERS.values()))
    new_dates = [d.strftime("%Y-%m-%d") for d in valid.index]

    if not new_dates:
        print("아직 확정된 신규 종가가 없습니다.")
        return

    existing = set(data["dates"])
    added = 0
    for d in valid.index:
        d_str = d.strftime("%Y-%m-%d")
        if d_str in existing:
            continue  # 안전장치: 혹시라도 겹치는 날짜는 건너뜀 (기존 값 보존)
        data["dates"].append(d_str)
        data["p1"].append(round(float(valid.loc[d, "QQQ"]), 4))
        data["p2"].append(round(float(valid.loc[d, "QLD"]), 4))
        data["p3"].append(round(float(valid.loc[d, "TQQQ"]), 4))
        added += 1

    if added == 0:
        print("추가할 새 날짜가 없습니다 (이미 반영됨).")
        return

    save_price_data(data)
    print(f"{added}일치 데이터 추가 완료. 새 마지막 날짜: {data['dates'][-1]} (총 {len(data['dates'])}일)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"업데이트 실패: {e}", file=sys.stderr)
        sys.exit(1)
