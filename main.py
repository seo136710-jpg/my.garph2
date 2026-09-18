import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# 앱 제목
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

# 데이터 불러오기 및 전처리 (캐싱 적용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # float/NaN 예외를 방지하는 안전한 문자열 추출 함수
    def get_first_item(val):
        if pd.isna(val) or val is None:
            return '미상'
        val_str = str(val).strip()
        if not val_str or val_str.lower() == 'nan':
            return '미상'
        return val_str.split('|')[0].strip()

    # 장르 전처리
    if 'genre' in df.columns:
        df['genre_first'] = df['genre'].apply(get_first_item)
    else:
        df['genre_first'] = '미상'
        
    # 제작 국가 전처리
    if 'nation' in df.columns:
        df['nation_clean'] = df['nation'].apply(get_first_item)
    else:
        df['nation_clean'] = '미상'
        
    return df

try:
    df = load_data()
    
    # ----------------------------------------------------
    # 그래프 1: 도넛 - 10위권에 든 영화의 장르 구성은 어떠한가
    # ----------------------------------------------------
    st.header("그래프1) 도넛 - 10위권에 든 영화의 장르 구성은 어떠한가")
    
    genre_counts = df['genre_first'].value_counts().reset_index()
    genre_counts.columns = ['장르', '편수']
    
    fig1 = px.pie(
        genre_counts,
        names='장르',
        values='편수',
        hole=0.4,
        title='장르별 영화 편수 비율 (도넛 그래프)',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig1.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>장르:</b> %{label}<br><b>영화 편수:</b> %{value}편<br><b>비율:</b> %{percent}<extra></extra>'
    )
    fig1.update_layout(showlegend=True, legend_title_text='장르')
    
    st.plotly_chart(fig1, use_container_width=True)
    st.divider()

    # ----------------------------------------------------
    # 그래프 2: 트리맵 - 장르 안에서 어떤 영화가 컸나
    # ----------------------------------------------------
    st.header("그래프2) 트리맵 - 장르 안에서 어떤 영화가 컸나")
    
    fig2 = px.treemap(
        df,
        path=[px.Constant("전체 영화"), 'genre_first', 'movieNm'],
        values='total_audi',
        color='genre_first',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title='장르 및 영화별 총 관객 수 트리맵'
    )
    fig2.update_traces(
        hovertemplate='<b>영화명/구분:</b> %{label}<br><b>총 관객 수:</b> %{value:,}명<extra></extra>'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    st.divider()

    # ----------------------------------------------------
    # 그래프 3: 히스토그램 (필수) — 영화 대부분은 관객이 몇 명쯤인가
    # ----------------------------------------------------
    st.header("그래프3) 히스토그램 (필수) — 영화 대부분은 관객이 몇 명쯤인가")
    
    fig3 = px.histogram(
        df,
        x='total_audi',
        nbins=30,
        title='총 관객 수(total_audi) 분포 히스토그램',
        labels={'total_audi': '총 관객 수', 'count': '영화 수'},
        color_discrete_sequence=['#636EFA']
    )
    fig3.update_traces(
        hovertemplate='<b>총 관객 수 구간:</b> %{x:,}명<br><b>영화 수:</b> %{y}편<extra></extra>'
    )
    fig3.update_layout(yaxis_title='영화 수(편)')
    
    st.plotly_chart(fig3, use_container_width=True)
    st.divider()

    # ----------------------------------------------------
    # 그래프 4: 산점도 (필수) — 스크린을 많이 받은 영화가 관객도 많나
    # ----------------------------------------------------
    st.header("그래프4) 산점도 (필수) — 스크린을 많이 받은 영화가 관객도 많나")
    
    fig4 = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        color='genre_first',
        hover_name='movieNm',
        labels={
            'first_scrn': '개봉일 스크린 수',
            'total_audi': '총 관객 수',
            'genre_first': '장르'
        },
        title='개봉일 스크린 수 vs 총 관객 수'
    )
    fig4.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,}개<br>총 관객 수: %{y:,}명<extra></extra>'
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    st.divider()

    # ----------------------------------------------------
    # 그래프 5: 박스플롯 (확장) — 장르별 관객 분포는 어떻게 다른가
    # ----------------------------------------------------
    st.header("그래프5) 박스플롯 (확장) — 장르별 관객 분포는 어떻게 다른가")
    
    genre_counts_series = df['genre_first'].value_counts()
    major_genres = genre_counts_series[genre_counts_series >= 10].index
    df_filtered = df[df['genre_first'].isin(major_genres)]
    
    fig5 = px.box(
        df_filtered,
        x='genre_first',
        y='total_audi',
        color='genre_first',
        hover_name='movieNm',
        labels={
            'genre_first': '장르',
            'total_audi': '총 관객 수'
        },
        title='주요 장르(10편 이상)별 총 관객 수 분포'
    )
    fig5.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>총 관객 수: %{y:,}명<extra></extra>'
    )
    fig5.update_layout(showlegend=False)
    
    st.plotly_chart(fig5, use_container_width=True)
    st.divider()

    # ----------------------------------------------------
    # 그래프 6: 버블 (확장) — 첫 주 관객까지 넣으면 무엇이 더 보이나
    # ----------------------------------------------------
    st.header("그래프6) 버블 (확장) — 첫 주 관객까지 넣으면 무엇이 더 보이나")
    
    fig6 = px.scatter(
        df,
        x='first_scrn',
        y='total_audi',
        color='genre_first',
        size='first_week_audi',
        hover_name='movieNm',
        labels={
            'first_scrn': '개봉일 스크린 수',
            'total_audi': '총 관객 수',
            'genre_first': '장르',
            'first_week_audi': '개봉 첫 주 관객 수'
        },
        title='개봉일 스크린 수 vs 총 관객 수 (원 크기: 개봉 첫 주 관객 수)'
    )
    fig6.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,}개<br>총 관객 수: %{y:,}명<extra></extra>'
    )
    
    st.plotly_chart(fig6, use_container_width=True)
    st.divider()

    # ----------------------------------------------------
    # 그래프 7: 선버스트 (심) — 국가에서 장르로 내려가면 무엇이 보이나
    # ----------------------------------------------------
    st.header("그래프7) 선버스트 (심) — 국가에서 장르로 내려가면 무엇이 보이나")
    
    nation_genre_counts = df.groupby(['nation_clean', 'genre_first']).size().reset_index(name='movie_count')
    
    fig7 = px.sunburst(
        nation_genre_counts,
        path=['nation_clean', 'genre_first'],
        values='movie_count',
        color='nation_clean',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title='제작 국가(nation) → 장르(genre)별 영화 편수 선버스트 차트'
    )
    fig7.update_traces(
        hovertemplate='<b>국가/장르:</b> %{label}<br><b>영화 편수:</b> %{value}편<extra></extra>'
    )
    
    st.plotly_chart(fig7, use_container_width=True)
    st.divider()

    # ----------------------------------------------------
    # 그래프 8: 자율 질문 — 스크린을 많이 확보한 영화가 상영 횟수도 많았는가
    # ----------------------------------------------------
    st.header("그래프8) 산점도 (자율) — 스크린을 많이 확보한 영화가 상영 횟수도 많았는가")
    
    fig8 = px.scatter(
        df,
        x='first_scrn',
        y='first_show',
        color='genre_first',
        hover_name='movieNm',
        labels={
            'first_scrn': '개봉일 스크린 수(first_scrn)',
            'first_show': '개봉일 상영 횟수(first_show)',
            'genre_first': '장르'
        },
        title='스크린을 많이 확보한 영화가 상영 횟수도 많았는가'
    )
    fig8.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,}개<br>개봉일 상영 횟수: %{y:,}회<extra></extra>'
    )
    
    st.plotly_chart(fig8, use_container_width=True)

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
