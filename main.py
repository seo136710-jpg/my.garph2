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
    
    # 안전한 첫 번째 요소 추출 함수
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
        
    # 제작 국가 전처리 (에러 발생 구역 방어 처리)
    if 'nation' in df.columns:
        df['nation_clean'] = df['nation'].apply(get_first_item)
    else:
        df['nation_clean'] = '미상'
        
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
    # 구역 3: 총 관객 수 히스토그램
    # ----------------------------------------------------
    st.header("3. 총 관객 수 분포 (히스토그램)")
    
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
    
    top_movie = df.loc[df['total_audi'].idxmax()]
    top_movie_name = top_movie['movieNm']
    top_movie_audi = top_movie['total_audi']
    
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 대부분의 영화는 총 관객 수가 하위 구간(약 200만 명 이하)에 밀집되어 있는 쏠림 분포를 나타냅니다. 한편, 가장 많은 관객을 동원한 영화는 **'{top_movie_name}'**(총 {top_movie_audi:,}명)입니다.")

    st.divider()

    # ----------------------------------------------------
    # 구역 4: 개봉일 스크린 수 vs 총 관객 수 (산점도)
    # ----------------------------------------------------
    st.header("4. 개봉일 스크린 수와 총 관객 수의 관계")
    
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
        title='개봉일 스크린 수(first_scrn) vs 총 관객 수(total_audi)'
    )
    fig4.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,}개<br>총 관객 수: %{y:,}명<extra></extra>'
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린 수가 많을수록 대체로 총 관객 수가 늘어나는 양의 상관관계를 보이며, 초기 스크린 확보량이 흥행의 주요 기반이 됨을 파악할 수 있습니다.")

    st.divider()

    # ----------------------------------------------------
    # 구역 5: 10편 이상 장르의 총 관객 수 상자 그림 (박스플롯)
    # ----------------------------------------------------
    st.header("5. 주요 장르별 총 관객 수 분포 비교 (박스플롯)")
    
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
    
    st.info("💡 **이 그래프로 알 수 있는 것:** 장르별 관객 수의 중앙값과 편차 범위를 비교할 수 있으며, 상자 밖의 이상치 점들을 통해 특정 대형 대박 작품이 속한 장르와 그 영향력을 파악할 수 있습니다.")

    st.divider()

    # ----------------------------------------------------
    # 구역 6: 개봉일 스크린 수 vs 총 관객 수 (버블 차트 - 원 크기: 개봉 첫 주 관객 수)
    # ----------------------------------------------------
    st.header("6. 개봉일 스크린 수, 총 관객 수, 개봉 첫 주 관객 수의 관계 (버블 차트)")
    
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
    
    st.info("💡 **이 그래프로 알 수 있는 것:** 스크린 수가 비슷하더라도 개봉 첫 주 관객(원 크기)이 큰 영화일수록 최종 총 관객 수 역시 크게 증가하는 양상을 입체적으로 한눈에 비교할 수 있습니다.")

    st.divider()

    # ----------------------------------------------------
    # 구역 7: 제작 국가별 장르 분포 (선버스트 차트)
    # ----------------------------------------------------
    st.header("7. 제작 국가 및 장르별 영화 편수 분포 (선버스트 차트)")
    
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
    
    st.info("💡 **이 그래프로 알 수 있는 것:** 제작 국가별 전체 점유율과 함께 각 국가 내에서 어떤 장르의 영화가 주로 제작·수입되는지의 계층적 비중을 한눈에 파악할 수 있습니다.")

    st.divider()

    # ----------------------------------------------------
    # 구역 8: 개봉 첫 주 관객 vs 총 관객 수 관계 (산점도)
    # ----------------------------------------------------
    st.header("8. 개봉 첫 주 관객과 총 관객 수의 관계")
    
    fig8 = px.scatter(
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
    fig8.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>개봉 첫 주 관객: %{x:,}명<br>총 관객: %{y:,}명<extra></extra>'
    )
    
    st.plotly_chart(fig8, use_container_width=True)
    
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉 첫 주 관객 수가 많을수록 총 관객 수도 증가하는 강한 양의 상관관계를 보이며, 초기 흥행 여파가 최종 성패에 결정적인 영향을 준다는 점을 파악할 수 있습니다.")

    st.divider()

    # ----------------------------------------------------
    # 구역 9: 주요 흥행 지표 간 상관관계 분석 (히트맵)
    # ----------------------------------------------------
    st.header("9. 흥행 지표 간 관계 분석")
    
    num_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
    available_cols = [c for c in num_cols if c in df.columns]
    
    if len(available_cols) > 1:
        corr = df[available_cols].corr()
        fig9 = px.imshow(
            corr,
            text_auto='.2f',
            color_continuous_scale='Blues',
            title='흥행 지표 간 상관계수 히트맵',
            labels=dict(x="지표", y="지표", color="상관계수")
        )
        st.plotly_chart(fig9, use_container_width=True)
        
        st.info("💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린 수, 상영 횟수, 초기 관객 수 및 톱10 유지 기간 사이의 밀접한 상관성을 통해 스크린 확보 수준이 흥행 유지력에 미치는 파급력을 비교 분석할 수 있습니다.")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
