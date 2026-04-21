import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time

# 페이지 설정
st.set_page_config(page_title="나라장터 통합 검색기", layout="wide")

# 사이드바 설정
st.sidebar.header("🔍 검색 조건 설정")

# 1. 키워드 설정 (OR 조건 검색)
default_keywords = "전자책, 오디오북, e북"
user_keywords = st.sidebar.text_input("검색 키워드 (쉼표로 구분하면 OR 검색)", value=default_keywords)
keywords = [k.strip() for k in user_keywords.split(",") if k.strip()]

# 2. 기간 설정 (기본 최근 6개월)
st.sidebar.subheader("📅 기간 설정")
default_start_date = datetime.now() - timedelta(days=180)
start_date = st.sidebar.date_input("시작일", value=default_start_date)
end_date = st.sidebar.date_input("종료일", value=datetime.now())

formatted_start = start_date.strftime('%Y/%m/%d')
formatted_end = end_date.strftime('%Y/%m/%d')

st.title("🏢 나라장터 입찰공고 스마트 모니터링 (v3.0)")
st.write(f"현재 설정: **{formatted_start} ~ {formatted_end}** 기간 동안 **{', '.join(keywords)}** (OR 조건) 검색")

if st.sidebar.button('🚀 공고 검색 시작'):
    all_results = []
    
    # 나라장터 보안 우회를 위한 강화된 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.g2b.go.kr/',
        'Connection': 'keep-alive'
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    # 세션 유지용 (차단 방지)
    session = requests.Session()

    for idx, kw in enumerate(keywords):
        status_text.text(f"'{kw}' 키워드로 검색 중... ({idx+1}/{len(keywords)})")
        try:
            # 나라장터 상세 검색 URL (OR 조건을 위해 키워드별 개별 호출)
            url = f"https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType=1&bidNm={kw}&searchDtType=1&fromBidDt={formatted_start}&toBidDt={formatted_end}&setMonth1=6"
            
            # 검색 사이 간격 (너무 빠르면 차단됨)
            time.sleep(1.5)
            
            res = session.get(url, headers=headers, timeout=20)
            res.encoding = 'euc-kr'
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                table = soup.find('table', {'class': 'table_list'})
                
                if table:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) > 7:
                            all_results.append({
                                "키워드": kw,
                                "공고명": cols[3].text.strip(),
                                "공고기관": cols[4].text.strip(),
                                "게시일(마감일)": cols[7].text.strip(),
                                "상태": cols[8].text.strip(),
                                "링크": "https://www.g2b.go.kr"
                            })
            else:
                st.warning(f"'{kw}' 키워드 응답 실패 (코드: {res.status_code})")
        
        except Exception as e:
            st.error(f"'{kw}' 검색 중 네트워크 오류가 발생했습니다.")
        
        progress_bar.progress((idx + 1) / len(keywords))

    status_text.text("검색 완료!")
    
    if all_results:
        df = pd.DataFrame(all_results).drop_duplicates(subset=['공고명'])
        df = df.sort_values(by="게시일(마감일)", ascending=False)
        st.success(f"총 {len(df)}건의 유효한 공고를 찾았습니다.")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 검색 결과 엑셀(CSV) 다운로드",
            data=csv,
            file_name=f"나라장터_검색_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
        )
    else:
        st.error("검색된 공고가 없습니다. 나라장터 서버가 현재 응답을 거부하고 있을 수 있습니다. 1~2분 후 다시 시도해 주세요.")

else:
    st.info("왼쪽 메뉴에서 조건을 설정하신 후 [공고 검색 시작] 버튼을 눌러주세요.")
