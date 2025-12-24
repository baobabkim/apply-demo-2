"""
데이터 분석 프로젝트 Streamlit 대시보드.

이 대시보드는 다음에 대한 인터랙티브 시각화를 제공합니다:
- 리텐션 분석
- A/B 테스트 결과
- 사용자 세그먼테이션
- 주요 인사이트 및 권장사항
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# Page configuration
st.set_page_config(
    page_title="데이터 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load analysis results
@st.cache_data
def load_analysis_results():
    """Load all analysis results from JSON files."""
    results = {}
    
    retention_path = "data/analysis_results/retention_analysis.json"
    ab_test_path = "data/analysis_results/ab_test_analysis.json"
    segment_path = "data/analysis_results/segment_analysis.json"
    
    if Path(retention_path).exists():
        with open(retention_path, 'r') as f:
            results['retention'] = json.load(f)
    
    if Path(ab_test_path).exists():
        with open(ab_test_path, 'r') as f:
            results['ab_test'] = json.load(f)
    
    if Path(segment_path).exists():
        with open(segment_path, 'r') as f:
            results['segment'] = json.load(f)
    
    return results


def show_overview(results):
    """Display overview page with key metrics."""
    st.title("📊 데이터 분석 대시보드")
    st.markdown("### 개요")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    if 'retention' in results:
        d7_retention = results['retention']['overall_retention']['D7']['retention_rate']
        with col1:
            st.metric("D7 리텐션", f"{d7_retention}%")
    
    if 'ab_test' in results:
        control_rate = results['ab_test']['group_a']['conversion_rate_pct']
        treatment_rate = results['ab_test']['group_b']['conversion_rate_pct']
        lift = results['ab_test']['effect_size']['relative_lift_pct']
        
        with col2:
            st.metric("대조군 전환율", f"{control_rate}%")
        
        with col3:
            st.metric("실험군 전환율", f"{treatment_rate}%", 
                     delta=f"{lift}%")
        
        p_value = results['ab_test']['statistical_tests']['z_test']['p_value']
        with col4:
            st.metric("P-value", f"{p_value:.4f}",
                     delta="유의함" if p_value < 0.05 else "유의하지 않음",
                     delta_color="normal" if p_value < 0.05 else "inverse")
    
    # Project Overview
    st.markdown("---")
    st.markdown("### 프로젝트 개요")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **가설:**
        가입 후 24시간 이내에 보상을 획득한 사용자는 훨씬 높은 리텐션율을 보일 것입니다.
        
        **방법론:**
        - 현실적인 행동 패턴을 가진 10,000명의 가상 사용자 생성
        - 리텐션 지표 추적 (D1, D3, D7, D14, D30)
        - 50:50 비율로 A/B 테스트 수행
        - K-means 클러스터링을 사용한 사용자 세그먼테이션
        """)
    
    with col2:
        if 'segment' in results:
            st.markdown(f"""
            **주요 통계:**
            - 총 사용자 수: {results['segment']['total_users']:,}명
            - 사용자 세그먼트: {results['segment']['n_clusters']}개
            - 분석 모듈: 3개 (리텐션, A/B 테스트, 세그먼테이션)
            - 통계 검정: Z-검정, 카이제곱, 클러스터링
            """)


def show_retention_analysis(results):
    """Display retention analysis page."""
    st.title("📈 리텐션 분석")
    
    if 'retention' not in results:
        st.warning("리텐션 분석 결과를 찾을 수 없습니다. 먼저 분석을 실행해주세요.")
        return
    
    retention_data = results['retention']
    
    # Overall Retention Metrics
    st.markdown("### 전체 리텐션 지표")
    
    retention_df = pd.DataFrame([
        {
            '일자': day,
            '리텐션율 (%)': metrics['retention_rate'],
            '리텐션 사용자': metrics['retained_users'],
            '총 사용자': metrics['total_users']
        }
        for day, metrics in retention_data['overall_retention'].items()
    ])
    
    # Retention curve
    fig = px.line(retention_df, x='일자', y='리텐션율 (%)',
                  title='리텐션 커브',
                  markers=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Retention table
    st.dataframe(retention_df, use_container_width=True)
    
    # Reward vs Non-Reward Comparison
    st.markdown("### 보상 vs 비보상 사용자")
    
    comparison_data = []
    for day, comp in retention_data['reward_comparison'].items():
        if 'reward' in comp and 'no_reward' in comp:
            comparison_data.append({
                '일자': day,
                '보상 사용자 (%)': comp['reward']['retention_rate'],
                '비보상 사용자 (%)': comp['no_reward']['retention_rate'],
                'P-value': comp.get('statistical_test', {}).get('p_value', None)
            })
    
    comp_df = pd.DataFrame(comparison_data)
    
    # Comparison chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=comp_df['일자'], y=comp_df['보상 사용자 (%)'],
                            mode='lines+markers', name='보상 사용자'))
    fig.add_trace(go.Scatter(x=comp_df['일자'], y=comp_df['비보상 사용자 (%)'],
                            mode='lines+markers', name='비보상 사용자'))
    fig.update_layout(title='리텐션: 보상 vs 비보상 사용자',
                     yaxis_title='리텐션율 (%)',
                     height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistical significance
    st.markdown("**통계적 유의성:**")
    st.dataframe(comp_df, use_container_width=True)
    
    st.info("💡 **인사이트:** 보상을 획듍한 사용자는 모든 기간에서 현저히 높은 리텐션을 보입니다 (p < 0.0001)")


def show_ab_test_results(results):
    """Display A/B test results page."""
    st.title("🧪 A/B 테스트 결과")
    
    if 'ab_test' not in results:
        st.warning("A/B 테스트 결과를 찾을 수 없습니다. 먼저 분석을 실행해주세요.")
        return
    
    ab_data = results['ab_test']
    
    # Conversion Rates
    st.markdown("### 전환율")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("대조군 (A)", 
                 f"{ab_data['group_a']['conversion_rate_pct']}%",
                 f"{ab_data['group_a']['conversions']}/{ab_data['group_a']['total_users']}")
    
    with col2:
        st.metric("실험군 (B)", 
                 f"{ab_data['group_b']['conversion_rate_pct']}%",
                 f"{ab_data['group_b']['conversions']}/{ab_data['group_b']['total_users']}")
    
    with col3:
        st.metric("상대적 상승률", 
                 f"{ab_data['effect_size']['relative_lift_pct']}%",
                 f"{ab_data['effect_size']['absolute_lift_pct']}pp 절대값")
    
    # Conversion comparison chart
    fig = go.Figure(data=[
        go.Bar(name='Control (A)', x=['Conversion Rate'], 
               y=[ab_data['group_a']['conversion_rate_pct']]),
        go.Bar(name='Treatment (B)', x=['Conversion Rate'], 
               y=[ab_data['group_b']['conversion_rate_pct']])
    ])
    fig.update_layout(title='전환율 비교', 
                     yaxis_title='전환율 (%)',
                     height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistical Tests
    st.markdown("### 통계 검정 결과")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Two-Proportion Z-검정:**")
        z_test = ab_data['statistical_tests']['z_test']
        st.write(f"- Z-점수: {z_test['z_score']}")
        st.write(f"- P-value: {z_test['p_value']}")
        st.write(f"- 유의함: {'✅ 예' if z_test['significant'] else '❌ 아니오'}")
    
    with col2:
        st.markdown("**카이제곱 검정:**")
        chi_test = ab_data['statistical_tests']['chi_square_test']
        st.write(f"- 카이제곱: {chi_test['chi_square']}")
        st.write(f"- P-value: {chi_test['p_value']}")
        st.write(f"- 유의함: {'✅ 예' if chi_test['significant'] else '❌ 아니오'}")
    
    # Effect Size and Confidence Interval
    st.markdown("### 효과 크기 & 신뢰구간")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**효과 크기 (Cohen's h):**")
        st.write(f"{ab_data['effect_size']['cohens_h']}")
        st.caption("소: 0.2, 중: 0.5, 대: 0.8")
    
    with col2:
        st.markdown("**95% 신뢰구간:**")
        ci = ab_data['confidence_interval_95']
        st.write(f"[{ci['lower']}%, {ci['upper']}%]")
    
    # Statistical Power
    st.markdown("### 통계적 검정력")
    power = ab_data['statistical_power']
    st.progress(power)
    st.write(f"검정력: {power:.2%} (목표: 80%)")
    
    # Recommendation
    st.markdown("### 권장사항")
    recommendation = ab_data['recommendation']
    
    if 'Deploy' in recommendation:
        st.success(f"✅ {recommendation}")
    else:
        st.warning(f"⚠️ {recommendation}")
        st.info("💡 테스트가 통계적 유의성에 도달하지 못했습니다. 테스트를 더 오래 실행하거나 샘플 크기를 늘리는 것을 고려하세요.")


def show_segment_analysis(results):
    """Display segment analysis page."""
    st.title("👥 사용자 세그먼테이션")
    
    if 'segment' not in results:
        st.warning("세그먼트 분석 결과를 찾을 수 없습니다. 먼저 분석을 실행해주세요.")
        return
    
    segment_data = results['segment']
    
    # Segment Distribution
    st.markdown("### 세그먼트 분포")
    
    segment_stats = pd.DataFrame(segment_data['segment_statistics'])
    
    # Pie chart
    fig = px.pie(segment_stats, values='size', names='cluster_id',
                 title='세그먼트별 사용자 분포')
    st.plotly_chart(fig, use_container_width=True)
    
    # Segment Characteristics
    st.markdown("### 세그먼트 특성")
    
    display_df = segment_stats[['cluster_id', 'size', 'percentage', 
                                 'avg_total_events', 'avg_reward_count', 
                                 'avg_daily_events']]
    display_df.columns = ['클러스터', '사용자 수', '%', '평균 이벤트', 
                          '평균 보상', '일일 평균 이벤트']
    st.dataframe(display_df, use_container_width=True)
    
    # Segment Retention
    st.markdown("### 세그먼트별 D7 리텐션")
    
    retention_df = pd.DataFrame(segment_data['segment_retention'])
    
    fig = px.bar(retention_df, x='cluster_id', y='d7_retention_rate',
                 title='세그먼트별 D7 리텐션',
                 labels={'cluster_id': '클러스터', 'd7_retention_rate': 'D7 리텐션 (%)'},
                 text='d7_retention_rate')
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Heterogeneous Treatment Effects
    if segment_data.get('heterogeneous_treatment_effects'):
        st.markdown("### 이질적 처치 효과 (HTE)")
        
        hte_df = pd.DataFrame(segment_data['heterogeneous_treatment_effects'])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Control', x=hte_df['cluster_id'], 
                            y=hte_df['control_conversion_rate']))
        fig.add_trace(go.Bar(name='Treatment', x=hte_df['cluster_id'], 
                            y=hte_df['treatment_conversion_rate']))
        fig.update_layout(title='세그먼트별 A/B 테스트 효과',
                         xaxis_title='클러스터',
                         yaxis_title='전환율 (%)',
                         height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(hte_df, use_container_width=True)
        
        st.info("💡 **인사이트:** 처치 효과는 세그먼트별로 다릅니다. 클러스터 0 (저참여 사용자)이 처치에 가장 강한 긍정적 반응을 보입니다.")


def show_insights(results):
    """Display insights and action items page."""
    st.title("💡 인사이트 & 액션 아이템")
    
    st.markdown("### 주요 발견사항")
    
    st.markdown("""
    1. **보상이 리텐션에 미치는 영향:**
       - 24시간 이내에 보상을 획듍한 사용자는 모든 기간에서 97%+ 리텐션을 보임
       - 비보상 사용자는 70-75% 리텐션을 보임
       - 차이는 통계적으로 매우 유의함 (p < 0.0001)
    
    2. **A/B 테스트 결과:**
       - 실험군은 전환율에서 6.69% 상대적 상승을 보임
       - 결과는 통계적으로 유의하지 않음 (p = 0.1152)
       - 통계적 검정력이 낮음 (35%), 더 큰 샘플 또는 더 긴 테스트 필요
    
    3. **사용자 세그먼테이션:**
       - 3개의 명확한 사용자 세그먼트 식별
       - 고참여 사용자 (클러스터 1): 11.7%, 200+ 평균 이벤트, 100% D7 리텐션
       - 중참여 사용자 (클러스터 2): 37.3%, 95 평균 이벤트, 99.9% D7 리텐션
       - 저참여 사용자 (클러스터 0): 51%, 30 평균 이벤트, 84% D7 리텐션
    """)
    
    st.markdown("### 권장 액션")
    
    st.markdown("""
    1. **보상 경험 최적화:**
       - 24시간 이내에 사용자가 첫 보상을 획듍하도록 우선순위 설정
       - 보상 획듍 활동으로 사용자를 안내하는 온보딩 플로우 구현
       - 환영 보너스 또는 더 쉽운 초기 보상 임계값 고려
    
    2. **개인화된 참여:**
       - 저참여 사용자(클러스터 0)에게 실험군 변형 타겟팅
       - 세그먼트별 푸시 알림 전략 생성
       - 보상을 획듍하지 못한 사용자를 위한 재참여 캠페인 개발
    
    3. **A/B 테스트 반복:**
       - 통계적 유의성에 도달하기 위해 테스트 계속 실행
       - 샘플 크기 증가 또는 테스트 기간 연장 고려
       - HTE 분석을 기반으로 세그먼트별 처치 탐색
    
    4. **리스크 완화:**
       - 고참여 사용자(클러스터 1)의 부정적 처치 효과 모니터링
       - 처치 배포 시 점진적 롤아웃 전략 구현
       - 리텐션 감소에 대한 자동 알림 설정
    """)
    
    st.markdown("### 제한사항 & 고려사항")
    
    st.warning("""
    - 데이터는 시연 목적으로 가상으로 생성됨
    - 실제 데이터는 다른 패턴을 보일 수 있음
    - 외부 요인(계절성, 마케팅 캠페인)이 고려되지 않음
    - 장기 리텐션(D60, D90)을 모니터링해야 함
    """)


# Main app
def main():
    """Main dashboard application."""
    
    # Sidebar navigation
    st.sidebar.title("내비게이션")
    page = st.sidebar.radio(
        "페이지 선택",
        ["개요", "리텐션 분석", "A/B 테스트 결과", 
         "사용자 세그먼테이션", "인사이트 & 액션"]
    )
    
    # Load data
    try:
        results = load_analysis_results()
        
        if not results:
            st.error("분석 결과를 찾을 수 없습니다. 먼저 분석 파이프라인을 실행해주세요:")
            st.code("python src/analysis/run_all_analysis.py")
            return
        
        # Display selected page
        if page == "개요":
            show_overview(results)
        elif page == "리텐션 분석":
            show_retention_analysis(results)
        elif page == "A/B 테스트 결과":
            show_ab_test_results(results)
        elif page == "사용자 세그먼테이션":
            show_segment_analysis(results)
        elif page == "인사이트 & 액션":
            show_insights(results)
    
    except Exception as e:
        st.error(f"결과 로딩 오류: {str(e)}")
        st.exception(e)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 정보")
    st.sidebar.info("""
    이 대시보드는 모바일 앱 시나리오에 대한 
    사용자 리텐션, A/B 테스트 결과, 
    사용자 세그먼테이션을 분석합니다.
    
    **기술 스택:**
    - Python, Pandas, NumPy
    - Scikit-learn, SciPy
    - Streamlit, Plotly
    """)


if __name__ == "__main__":
    main()
