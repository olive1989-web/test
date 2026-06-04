import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title='경쟁사 베스트 상품',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# CSS로 한글 폰트 설정
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
    * {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    body {
        background-color: #f8f9fa;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .metric-label {
        color: #666;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #2c3e50;
        font-size: 32px;
        font-weight: 700;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv('경쟁사_베스트_상품.csv')
    return df

df = load_data()

# 일별 시계열 데이터 생성
@st.cache_data
def generate_daily_sales():
    categories = df['카테고리'].unique()
    dates = pd.date_range(end=datetime.now().date(), periods=30, freq='D')

    daily_sales = []
    for date in dates:
        for category in categories:
            category_data = df[df['카테고리'] == category]
            # 판매량 기반 매출 (가격 * 판매량)
            daily_amount = (category_data['가격'] * category_data['판매량']).sum()
            # 날짜별로 약간의 변동 추가
            variation = np.random.normal(1.0, 0.15)
            daily_amount = int(daily_amount * variation * 0.1)  # 스케일 조정

            daily_sales.append({
                '날짜': date,
                '카테고리': category,
                '매출': max(0, daily_amount)
            })

    return pd.DataFrame(daily_sales)

daily_df = generate_daily_sales()

# 오늘, 어제, 전월 매출 계산
today = datetime.now().date()
yesterday = today - timedelta(days=1)
month_ago = today - timedelta(days=30)

today_sales = daily_df[daily_df['날짜'].dt.date == today]['매출'].sum()
yesterday_sales = daily_df[daily_df['날짜'].dt.date == yesterday]['매출'].sum()
month_sales = daily_df[daily_df['날짜'].dt.date >= month_ago]['매출'].sum()

def format_currency(value):
    """원화 형식으로 변환"""
    return f"₩{value:,.0f}"

# 페이지 제목
st.markdown("<h1>경쟁사 베스트 상품</h1>", unsafe_allow_html=True)

# 메트릭 카드
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">오늘</div>
        <div class="metric-value">{format_currency(today_sales)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">어제</div>
        <div class="metric-value">{format_currency(yesterday_sales)}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">전월</div>
        <div class="metric-value">{format_currency(month_sales)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 차트 영역
col1, col2 = st.columns(2)

# 왼쪽: 일별 매출 추이
with col1:
    daily_total = daily_df.groupby('날짜')['매출'].sum().reset_index()

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=daily_total['날짜'],
        y=daily_total['매출'],
        mode='lines+markers',
        name='매출',
        line=dict(color='#4a7c9e', width=3),
        marker=dict(size=6, color='#4a7c9e'),
        fill='tozeroy',
        fillcolor='rgba(74, 124, 158, 0.1)',
        hovertemplate='<b>%{x|%m월 %d일}</b><br>매출: ₩%{y:,.0f}<extra></extra>'
    ))

    fig_line.update_layout(
        title='일별 매출 추이',
        xaxis_title='날짜',
        yaxis_title='매출',
        hovermode='x unified',
        plot_bgcolor='rgba(248, 249, 250, 0.5)',
        paper_bgcolor='white',
        font=dict(family='Noto Sans KR', size=12, color='#2c3e50'),
        height=400,
        margin=dict(l=50, r=20, t=50, b=50)
    )

    fig_line.update_yaxes(
        tickformat='$,.0f',
        tickprefix='₩',
        gridcolor='rgba(200, 200, 200, 0.2)'
    )

    st.plotly_chart(fig_line, use_container_width=True)

# 오른쪽: 카테고리별 매출 비중
with col2:
    category_sales = df.groupby('카테고리').apply(
        lambda x: (x['가격'] * x['판매량']).sum()
    ).reset_index(name='매출')

    colors = ['#4a7c9e', '#6b8dbf', '#8da3c4', '#b0becd', '#d4dae5',
              '#5a8daf', '#7a9dc0', '#9aadd1', '#c0c8db']

    fig_pie = go.Figure(data=[go.Pie(
        labels=category_sales['카테고리'],
        values=category_sales['매출'],
        marker=dict(colors=colors[:len(category_sales)]),
        textposition='inside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>매출: ₩%{value:,.0f}<br>비중: %{percent}<extra></extra>',
        textfont=dict(family='Noto Sans KR', size=11, color='white')
    )])

    fig_pie.update_layout(
        title='카테고리별 매출 비중',
        paper_bgcolor='white',
        font=dict(family='Noto Sans KR', size=12, color='#2c3e50'),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig_pie, use_container_width=True)

# 하단 데이터 테이블
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("상품 정보")

display_df = df[['경쟁사명', '상품명', '카테고리', '가격', '판매량', '평점']].copy()
display_df['가격'] = display_df['가격'].apply(lambda x: f"₩{x:,}")
display_df['판매량'] = display_df['판매량'].apply(lambda x: f"{x:,}")

st.dataframe(display_df, use_container_width=True, hide_index=True)
