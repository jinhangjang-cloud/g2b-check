import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="나라장터 6개월 모니터링", layout="wide")

st.title("🏢 나라장터 공고 모니터링 (최근 6개월)")
st.info("검색 키워드: '오디오북', '전자책', 'e북'")

if st.button('최근 6개월 사업 공고 찾기'):
    # 검색 날짜 설정 (오늘로부터 180일 전)
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y/%m/%d')
    today = datetime.now().strftime('%Y/%m/%d')
    
    keywords = ['오디오북', '전자책', 'e북']
    all_results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://www.g2b.go.kr/'
    }
    
    with st.spinner(f'{six_months_ago} 부터 현재까지의 데이터를 조회 중입니다...'):
        for kw in keywords:
            try:
                # 최근 6개월간 공고를 조회하는 특수 URL
                url = f"https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType=1&bidNm={kw}&searchDtType=1&fromBidDt={six_months_ago}&toBidDt={today}&setMonth1=6"
                
                res = requests.get(url, headers=headers, timeout=15)
                res.encoding = 'euc-kr'
                
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
                                "공고일(마감일)": cols[7].text.strip(),
                                "상태": cols[8].text.strip()
                            })
            except:
                continue # 오류 나면 다음 키워드로 패스
    
    if all_results:
        df = pd.DataFrame(all_results).drop_duplicates(subset=['공고명'])
        # 날짜순으로 정렬
        df = df.sort_values(by="공고일(마감일)", ascending=False)
        st.success(f"최근 6개월간 총 {len(df)}건의 사업이 검색되었습니다.")
        st.dataframe(df, use_container_width=True)
    else:
        st.error("현재 나라장터 서버 접속이 원활하지 않습니다. 1~2분 후 다시 시도해 주세요.")

st.caption(f"※ 조회 범위: {six_months_ago} ~ {today}")
