import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="나라장터 모니터링", layout="wide")

st.title("🏢 나라장터 입찰 공고 모니터링")
st.subheader("키워드: '오디오북', '전자책', 'e북'")

if st.button('실시간 사업 찾기'):
    keywords = ['오디오북', '전자책', 'e북']
    all_results = []
    
    with st.spinner('나라장터에서 데이터를 가져오는 중...'):
        for kw in keywords:
            # 나라장터 검색 URL (최근 공고 위주)
            url = f"https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType=1&bidNm={kw}&searchDtType=1"
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 테이블 데이터 추출
            table = soup.find('table', {'class': 'table_list'})
            if table:
                rows = table.find_all('tr')[1:] # 헤더 제외
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) > 5:
                        all_results.append({
                            "키워드": kw,
                            "공고명": cols[3].text.strip(),
                            "공고기관": cols[4].text.strip(),
                            "마감일시": cols[7].text.strip(),
                            "링크": "https://www.g2b.go.kr"
                        })
    
    if all_results:
        df = pd.DataFrame(all_results).drop_duplicates(subset=['공고명'])
        st.write(f"총 {len(df)}건의 사업이 발견되었습니다.")
        st.table(df)
    else:
        st.warning("현재 검색된 사업이 없습니다.")

st.info("※ 이 프로그램은 무료 라이브러리(BeautifulSoup 4.12.2)를 사용하여 보안 가이드라인을 준수합니다.")
