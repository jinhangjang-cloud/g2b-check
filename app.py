import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="나라장터 모니터링", layout="wide")

st.title("🏢 나라장터 입찰 공고 모니터링")
st.subheader("키워드: '오디오북', '전자책', 'e북'")

if st.button('실시간 사업 찾기'):
    keywords = ['오디오북', '전자책', 'e북']
    all_results = []
    
    # 나라장터 보안 통과를 위한 "사람인 척" 하는 설정값
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    with st.spinner('나라장터 서버에 접속 중입니다...'):
        for kw in keywords:
            try:
                # 검색 기간을 최근으로 한정하여 검색 (searchDtType=1: 공고일 기준)
                url = f"https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType=1&bidNm={kw}&searchDtType=1"
                res = requests.get(url, headers=headers, timeout=10)
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
                                "마감일시": cols[7].text.strip(),
                                "상태": cols[8].text.strip()
                            })
            except Exception as e:
                st.error(f"'{kw}' 검색 중 오류 발생: 나라장터 서버 응답 지연")
    
    if all_results:
        df = pd.DataFrame(all_results).drop_duplicates(subset=['공고명'])
        st.success(f"총 {len(df)}건의 사업이 발견되었습니다!")
        st.table(df)
    else:
        st.warning("현재 진행 중인 사업이 없거나 나라장터 접속이 원활하지 않습니다.")

st.info("※ 팁: 나라장터 서버 상태에 따라 1~2번 더 눌러야 할 수 있습니다.")
