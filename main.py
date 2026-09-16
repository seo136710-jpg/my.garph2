import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# 앱 제목 및 설명
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("KOBIS 박스오피스 데이터를 바탕으로 영화 시장의 분포와 다양한 상관관계를 탐색합니다.")

# 데이터 불러오기 및 전처리 (캐싱 적용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # 장르 전처리 (세로막대 기호 '|' 기준 첫 번째 장르만 추출)
    if 'genre' in df.columns:
        df['genre_first'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip())
    else:
        df['genre_first'] = '미상'
        
    return df

try:
    df = load_data()
    
    # ----------------------------------------------------
    # 구역 1: 장르별 영화 편수 (도넛 그래프)
    # ----------------------------------------------------
    st.header("1. 장르별 영화 편수 분포")
    
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
    fig1.update_layout(
        showlegend=True,
        legend_title_text='장르'
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    st.info("💡 **이 그래프로 알 수 있는 것:** 특정 주요 장르에 상위권 박스오피스 영화 편수가 집중되어 있으며, 장르별 시장 점유 비율을 한눈에 비교할 수 있습니다.")
    
    st.divider()

    # ----------------------------------------------------
    # 구역 2: 장르 및 영화별 총 관객 수 (트리맵)
    # ----------------------------------------------------
    st.header("2. 장르 및 영화별 총 관객 수 분포 (트리맵)")
    
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
    
    st.info("💡 **이 그래프로 알 수 있는 것:** 장르별 총 관객 점유율 파악과 동시에 특정 흥행작이 속한 장르의 전체 흥행 실적을 견인하는 비중을 직관적으로 확인할 수 있습니다.")

    st.divider()

    # ----------------------------------------------------
    # 구역 3: 개봉 첫 주 관객 vs 총 관객 수 관계 (산점도)
    # ----------------------------------------------------
    st.header("3. 개봉 첫 주 관객과 총 관객 수의 관계")
    
    fig3 = px.scatter(
        df,
        x='first_week_audi',
        y='total_audi',
        color='genre_first',
        size='first_scrn',
        hover_name='movieNm',
        labels={
            'first_week_audi': '개봉 첫 주 관객 수',
            'total_audi': '총 관객 수',
            'genre_first': '장르',
            'first_scrn': '개봉일 스크린 수'
        },
        title='개봉 첫 주 관객 수 vs 총 관객 수 (원 크기: 개봉일 스크린 수)'
    )
    fig3.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>개봉 첫 주 관객: %{x:,}명<br>총 관객: %{y:,}명<extra></extra>'
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉 첫 주 관객 수가 많을수록 총 관객 수도 증가하는 강한 양의 상관관계를 보이며, 초기 흥행 여파가 최종 성패에 결정적인 영향을 준다는 점을 파악할 수 있습니다.")

    st.divider()

    # ----------------------------------------------------
    # 구역 4: 주요 흥행 지표 간 상관관계 분석 (히트맵)
    # ----------------------------------------------------
    st.header("4. 흥행 지표 간 관계 분석")
    
    num_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
    available_cols = [c for c in num_cols if c in df.columns]
    
    if len(available_cols) > 1:
        corr = df[available_cols].corr()
        fig4 = px.imshow(
            corr,
            text_auto='.2f',
            color_continuous_scale='Blues',
            title='흥행 지표 간 상관계수 히트맵',
            labels=dict(x="지표", y="지표", color="상관계수")
        )
        st.plotly_chart(fig4, use_container_width=True)
        
        st.info("💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린 수, 상영 횟수, 초기 관객 수 및 톱10 유지 기간 사이의 밀접한 상관성을 통해 스크린 확보 수준이 흥행 유지력에 미치는 파급력을 비교 분석할 수 있습니다.")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
