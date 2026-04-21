import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="나라장터 통합 검색기", layout="wide")

# 사이드바: 검색 조건 설정
st.sidebar.header("🔍 검색 조건 설정")

# 1. 키워드 설정 (기본값 제공)
default_keywords = "전자책, 오디오북, e북"
user_keywords = st.sidebar.text_input("검색 키워드 (쉼표로 구분)", value=default_keywords)
keywords = [k.strip() for k in user_keywords.split(",")]

# 2. 기간 설정 (기본값: 최근 6개월)
st.sidebar.subheader("📅 기간 설정")
default_start_date = datetime.now() - timedelta(days=180)
start_date = st.sidebar.date_input("시작일", value=default_start_date)
end_date = st.sidebar.date_input("종료일", value=datetime.now())

# 날짜 형식 변환 (나라장터 규격: YYYY/MM/DD)
formatted_start = start_date.strftime('%Y/%m/%d')
formatted_end = end_date.strftime('%Y/%m/%d')

st.title("🏢 나라장터 입찰공고 스마트 모니터링")
st.write(f"현재 설정: **{formatted_start} ~ {formatted_end}** 기간 동안 **{', '.join(keywords)}** 검색")

# 검색 버튼
if st.sidebar.button('🚀 공고 검색 시작'):
    all_results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://www.g2b.go.kr/'
    }
    
    progress_bar = st.progress(0)
    for idx, kw in enumerate(keywords):
        try:
            # 사용자가 설정한 기간과 키워드로 URL 생성
            url = f"https://www.g2b.go.kr:8101/ep/tbid/tbidList.do?searchType=1&bidNm={kw}&searchDtType=1&fromBidDt={formatted_start}&toBidDt={formatted_end}&setMonth1=6"
            
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
                            "수요기관": cols[5].text.strip(),
                            "게시일(마감일)": cols[7].text.strip(),
                            "상태": cols[8].text.strip()
                        })
            progress_bar.progress((idx + 1) / len(keywords))
        except:
            st.warning(f"'{kw}' 키워드 조회 중 연결 지연이 발생했습니다.")
    
    if all_results:
        df = pd.DataFrame(all_results).drop_duplicates(subset=['공고명'])
        df = df.sort_values(by="게시일(마감일)", ascending=False)
        st.success(f"총 {len(df)}건의 공고를 찾았습니다.")
        
        # 결과 테이블 출력
        st.dataframe(df, use_container_width=True)
        
        # 엑셀 다운로드 기능 추가
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 검색 결과 엑셀(CSV) 다운로드",
            data=csv,
            file_name=f"나라장터_검색결과_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
        )
    else:
        st.error("검색 결과가 없습니다. 기간이나 키워드를 조정해 보세요.")

else:
    st.info("왼쪽 메뉴에서 조건을 확인하신 후 [공고 검색 시작] 버튼을 눌러주세요.")
