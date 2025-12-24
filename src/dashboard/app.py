"""
Streamlit Dashboard for Data Analysis Project.

This dashboard provides interactive visualizations for:
- Retention analysis
- A/B test results
- User segmentation
- Key insights and recommendations
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# Page configuration
st.set_page_config(
    page_title="Data Analysis Dashboard",
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
    st.title("📊 Data Analysis Dashboard")
    st.markdown("### Overview")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    if 'retention' in results:
        d7_retention = results['retention']['overall_retention']['D7']['retention_rate']
        with col1:
            st.metric("D7 Retention", f"{d7_retention}%")
    
    if 'ab_test' in results:
        control_rate = results['ab_test']['group_a']['conversion_rate_pct']
        treatment_rate = results['ab_test']['group_b']['conversion_rate_pct']
        lift = results['ab_test']['effect_size']['relative_lift_pct']
        
        with col2:
            st.metric("Control Conversion", f"{control_rate}%")
        
        with col3:
            st.metric("Treatment Conversion", f"{treatment_rate}%", 
                     delta=f"{lift}%")
        
        p_value = results['ab_test']['statistical_tests']['z_test']['p_value']
        with col4:
            st.metric("P-value", f"{p_value:.4f}",
                     delta="Significant" if p_value < 0.05 else "Not Significant",
                     delta_color="normal" if p_value < 0.05 else "inverse")
    
    # Project Overview
    st.markdown("---")
    st.markdown("### Project Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Hypothesis:**
        Users who earn rewards within 24 hours of signup will have significantly higher retention rates.
        
        **Methodology:**
        - Generated 10,000 synthetic users with realistic behavior patterns
        - Tracked retention metrics (D1, D3, D7, D14, D30)
        - Conducted A/B test with 50:50 split
        - Performed user segmentation using K-means clustering
        """)
    
    with col2:
        if 'segment' in results:
            st.markdown(f"""
            **Key Statistics:**
            - Total Users: {results['segment']['total_users']:,}
            - User Segments: {results['segment']['n_clusters']}
            - Analysis Modules: 3 (Retention, A/B Test, Segmentation)
            - Statistical Tests: Z-test, Chi-square, Clustering
            """)


def show_retention_analysis(results):
    """Display retention analysis page."""
    st.title("📈 Retention Analysis")
    
    if 'retention' not in results:
        st.warning("Retention analysis results not found. Please run the analysis first.")
        return
    
    retention_data = results['retention']
    
    # Overall Retention Metrics
    st.markdown("### Overall Retention Metrics")
    
    retention_df = pd.DataFrame([
        {
            'Day': day,
            'Retention Rate (%)': metrics['retention_rate'],
            'Retained Users': metrics['retained_users'],
            'Total Users': metrics['total_users']
        }
        for day, metrics in retention_data['overall_retention'].items()
    ])
    
    # Retention curve
    fig = px.line(retention_df, x='Day', y='Retention Rate (%)',
                  title='Retention Curve',
                  markers=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Retention table
    st.dataframe(retention_df, use_container_width=True)
    
    # Reward vs Non-Reward Comparison
    st.markdown("### Reward vs Non-Reward Users")
    
    comparison_data = []
    for day, comp in retention_data['reward_comparison'].items():
        if 'reward' in comp and 'no_reward' in comp:
            comparison_data.append({
                'Day': day,
                'Reward Users (%)': comp['reward']['retention_rate'],
                'No Reward Users (%)': comp['no_reward']['retention_rate'],
                'P-value': comp.get('statistical_test', {}).get('p_value', None)
            })
    
    comp_df = pd.DataFrame(comparison_data)
    
    # Comparison chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=comp_df['Day'], y=comp_df['Reward Users (%)'],
                            mode='lines+markers', name='Reward Users'))
    fig.add_trace(go.Scatter(x=comp_df['Day'], y=comp_df['No Reward Users (%)'],
                            mode='lines+markers', name='No Reward Users'))
    fig.update_layout(title='Retention: Reward vs No Reward Users',
                     yaxis_title='Retention Rate (%)',
                     height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistical significance
    st.markdown("**Statistical Significance:**")
    st.dataframe(comp_df, use_container_width=True)
    
    st.info("💡 **Insight:** Users who earn rewards show significantly higher retention across all time periods (p < 0.0001)")


def show_ab_test_results(results):
    """Display A/B test results page."""
    st.title("🧪 A/B Test Results")
    
    if 'ab_test' not in results:
        st.warning("A/B test results not found. Please run the analysis first.")
        return
    
    ab_data = results['ab_test']
    
    # Conversion Rates
    st.markdown("### Conversion Rates")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Control (A)", 
                 f"{ab_data['group_a']['conversion_rate_pct']}%",
                 f"{ab_data['group_a']['conversions']}/{ab_data['group_a']['total_users']}")
    
    with col2:
        st.metric("Treatment (B)", 
                 f"{ab_data['group_b']['conversion_rate_pct']}%",
                 f"{ab_data['group_b']['conversions']}/{ab_data['group_b']['total_users']}")
    
    with col3:
        st.metric("Relative Lift", 
                 f"{ab_data['effect_size']['relative_lift_pct']}%",
                 f"{ab_data['effect_size']['absolute_lift_pct']}pp absolute")
    
    # Conversion comparison chart
    fig = go.Figure(data=[
        go.Bar(name='Control (A)', x=['Conversion Rate'], 
               y=[ab_data['group_a']['conversion_rate_pct']]),
        go.Bar(name='Treatment (B)', x=['Conversion Rate'], 
               y=[ab_data['group_b']['conversion_rate_pct']])
    ])
    fig.update_layout(title='Conversion Rate Comparison', 
                     yaxis_title='Conversion Rate (%)',
                     height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistical Tests
    st.markdown("### Statistical Test Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Two-Proportion Z-Test:**")
        z_test = ab_data['statistical_tests']['z_test']
        st.write(f"- Z-score: {z_test['z_score']}")
        st.write(f"- P-value: {z_test['p_value']}")
        st.write(f"- Significant: {'✅ Yes' if z_test['significant'] else '❌ No'}")
    
    with col2:
        st.markdown("**Chi-Square Test:**")
        chi_test = ab_data['statistical_tests']['chi_square_test']
        st.write(f"- Chi-square: {chi_test['chi_square']}")
        st.write(f"- P-value: {chi_test['p_value']}")
        st.write(f"- Significant: {'✅ Yes' if chi_test['significant'] else '❌ No'}")
    
    # Effect Size and Confidence Interval
    st.markdown("### Effect Size & Confidence Interval")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Effect Size (Cohen's h):**")
        st.write(f"{ab_data['effect_size']['cohens_h']}")
        st.caption("Small: 0.2, Medium: 0.5, Large: 0.8")
    
    with col2:
        st.markdown("**95% Confidence Interval:**")
        ci = ab_data['confidence_interval_95']
        st.write(f"[{ci['lower']}%, {ci['upper']}%]")
    
    # Statistical Power
    st.markdown("### Statistical Power")
    power = ab_data['statistical_power']
    st.progress(power)
    st.write(f"Power: {power:.2%} (Target: 80%)")
    
    # Recommendation
    st.markdown("### Recommendation")
    recommendation = ab_data['recommendation']
    
    if 'Deploy' in recommendation:
        st.success(f"✅ {recommendation}")
    else:
        st.warning(f"⚠️ {recommendation}")
        st.info("💡 The test did not reach statistical significance. Consider running the test longer or increasing sample size.")


def show_segment_analysis(results):
    """Display segment analysis page."""
    st.title("👥 User Segmentation")
    
    if 'segment' not in results:
        st.warning("Segment analysis results not found. Please run the analysis first.")
        return
    
    segment_data = results['segment']
    
    # Segment Distribution
    st.markdown("### Segment Distribution")
    
    segment_stats = pd.DataFrame(segment_data['segment_statistics'])
    
    # Pie chart
    fig = px.pie(segment_stats, values='size', names='cluster_id',
                 title='User Distribution by Segment')
    st.plotly_chart(fig, use_container_width=True)
    
    # Segment Characteristics
    st.markdown("### Segment Characteristics")
    
    display_df = segment_stats[['cluster_id', 'size', 'percentage', 
                                 'avg_total_events', 'avg_reward_count', 
                                 'avg_daily_events']]
    display_df.columns = ['Cluster', 'Users', '%', 'Avg Events', 
                          'Avg Rewards', 'Avg Daily Events']
    st.dataframe(display_df, use_container_width=True)
    
    # Segment Retention
    st.markdown("### Segment-Specific D7 Retention")
    
    retention_df = pd.DataFrame(segment_data['segment_retention'])
    
    fig = px.bar(retention_df, x='cluster_id', y='d7_retention_rate',
                 title='D7 Retention by Segment',
                 labels={'cluster_id': 'Cluster', 'd7_retention_rate': 'D7 Retention (%)'},
                 text='d7_retention_rate')
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Heterogeneous Treatment Effects
    if segment_data.get('heterogeneous_treatment_effects'):
        st.markdown("### Heterogeneous Treatment Effects (HTE)")
        
        hte_df = pd.DataFrame(segment_data['heterogeneous_treatment_effects'])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Control', x=hte_df['cluster_id'], 
                            y=hte_df['control_conversion_rate']))
        fig.add_trace(go.Bar(name='Treatment', x=hte_df['cluster_id'], 
                            y=hte_df['treatment_conversion_rate']))
        fig.update_layout(title='A/B Test Effect by Segment',
                         xaxis_title='Cluster',
                         yaxis_title='Conversion Rate (%)',
                         height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(hte_df, use_container_width=True)
        
        st.info("💡 **Insight:** Treatment effect varies by segment. Cluster 0 (low-engagement users) shows the strongest positive response to the treatment.")


def show_insights(results):
    """Display insights and action items page."""
    st.title("💡 Insights & Action Items")
    
    st.markdown("### Key Findings")
    
    st.markdown("""
    1. **Reward Impact on Retention:**
       - Users earning rewards within 24 hours show 97%+ retention across all periods
       - Non-reward users show 70-75% retention
       - Difference is highly statistically significant (p < 0.0001)
    
    2. **A/B Test Results:**
       - Treatment group shows 6.69% relative lift in conversion
       - Result is not statistically significant (p = 0.1152)
       - Statistical power is low (35%), suggesting need for larger sample or longer test
    
    3. **User Segmentation:**
       - Three distinct user segments identified
       - High-engagement users (Cluster 1): 11.7%, 200+ avg events, 100% D7 retention
       - Medium-engagement users (Cluster 2): 37.3%, 95 avg events, 99.9% D7 retention
       - Low-engagement users (Cluster 0): 51%, 30 avg events, 84% D7 retention
    """)
    
    st.markdown("### Recommended Actions")
    
    st.markdown("""
    1. **Optimize Reward Experience:**
       - Prioritize getting users to earn their first reward within 24 hours
       - Implement onboarding flow that guides users to reward-earning activities
       - Consider welcome bonus or easier initial reward thresholds
    
    2. **Personalized Engagement:**
       - Target low-engagement users (Cluster 0) with treatment variant
       - Create segment-specific push notification strategies
       - Develop re-engagement campaigns for users who haven't earned rewards
    
    3. **A/B Test Iteration:**
       - Continue running the test to reach statistical significance
       - Consider increasing sample size or test duration
       - Explore segment-specific treatments based on HTE analysis
    
    4. **Risk Mitigation:**
       - Monitor high-engagement users (Cluster 1) for any negative treatment effects
       - Implement gradual rollout strategy if deploying treatment
       - Set up automated alerts for retention drops
    """)
    
    st.markdown("### Limitations & Considerations")
    
    st.warning("""
    - Data is synthetically generated for demonstration purposes
    - Real-world data may show different patterns
    - External factors (seasonality, marketing campaigns) not accounted for
    - Longer-term retention (D60, D90) should be monitored
    """)


# Main app
def main():
    """Main dashboard application."""
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Overview", "Retention Analysis", "A/B Test Results", 
         "User Segmentation", "Insights & Actions"]
    )
    
    # Load data
    try:
        results = load_analysis_results()
        
        if not results:
            st.error("No analysis results found. Please run the analysis pipeline first:")
            st.code("python src/analysis/run_all_analysis.py")
            return
        
        # Display selected page
        if page == "Overview":
            show_overview(results)
        elif page == "Retention Analysis":
            show_retention_analysis(results)
        elif page == "A/B Test Results":
            show_ab_test_results(results)
        elif page == "User Segmentation":
            show_segment_analysis(results)
        elif page == "Insights & Actions":
            show_insights(results)
    
    except Exception as e:
        st.error(f"Error loading results: {str(e)}")
        st.exception(e)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info("""
    This dashboard analyzes user retention, A/B test results, 
    and user segmentation for a mobile app scenario.
    
    **Tech Stack:**
    - Python, Pandas, NumPy
    - Scikit-learn, SciPy
    - Streamlit, Plotly
    """)


if __name__ == "__main__":
    main()
