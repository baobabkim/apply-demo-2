"""
Generate static HTML dashboard for GitHub Pages deployment.

This script creates a standalone HTML file with all visualizations
that can be deployed to GitHub Pages.
"""

import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path


def load_analysis_results():
    """Load all analysis results from JSON files."""
    results = {}
    
    retention_path = "data/analysis_results/retention_analysis.json"
    ab_test_path = "data/analysis_results/ab_test_analysis.json"
    segment_path = "data/analysis_results/segment_analysis.json"
    
    if Path(retention_path).exists():
        with open(retention_path, 'r', encoding='utf-8') as f:
            results['retention'] = json.load(f)
    
    if Path(ab_test_path).exists():
        with open(ab_test_path, 'r', encoding='utf-8') as f:
            results['ab_test'] = json.load(f)
    
    if Path(segment_path).exists():
        with open(segment_path, 'r', encoding='utf-8') as f:
            results['segment'] = json.load(f)
    
    return results


def create_static_dashboard():
    """Create static HTML dashboard with all visualizations."""
    
    results = load_analysis_results()
    
    if not results:
        print("[WARNING] 분석 결과를 찾을 수 없습니다. 먼저 분석을 실행하세요.")
        return
    
    # Create figure with subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            '리텐션 커브', '보상 vs 비보상 사용자',
            '전환율 비교', '세그먼트별 D7 리텐션',
            '세그먼트 분포', 'A/B 테스트 효과 (세그먼트별)'
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "pie"}, {"type": "bar"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )
    
    # 1. Retention Curve
    if 'retention' in results:
        retention_data = results['retention']['overall_retention']
        days = list(retention_data.keys())
        rates = [retention_data[day]['retention_rate'] for day in days]
        
        fig.add_trace(
            go.Scatter(x=days, y=rates, mode='lines+markers', name='전체 리텐션',
                      line=dict(color='#FF4B4B', width=3)),
            row=1, col=1
        )
        
        # 2. Reward vs Non-Reward
        reward_comp = results['retention']['reward_comparison']
        days = list(reward_comp.keys())
        reward_rates = [reward_comp[day].get('reward', {}).get('retention_rate', 0) for day in days]
        no_reward_rates = [reward_comp[day].get('no_reward', {}).get('retention_rate', 0) for day in days]
        
        fig.add_trace(
            go.Scatter(x=days, y=reward_rates, mode='lines+markers', name='보상 유저',
                      line=dict(color='#00CC96', width=2)),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=days, y=no_reward_rates, mode='lines+markers', name='비보상 유저',
                      line=dict(color='#AB63FA', width=2)),
            row=1, col=2
        )
    
    # 3. A/B Test Conversion
    if 'ab_test' in results:
        ab_data = results['ab_test']
        fig.add_trace(
            go.Bar(x=['대조군 (A)', '실험군 (B)'],
                  y=[ab_data['group_a']['conversion_rate_pct'],
                     ab_data['group_b']['conversion_rate_pct']],
                  name='전환율',
                  marker_color=['#636EFA', '#EF553B'],
                  text=[f"{ab_data['group_a']['conversion_rate_pct']}%",
                        f"{ab_data['group_b']['conversion_rate_pct']}%"],
                  textposition='outside'),
            row=2, col=1
        )
    
    # 4. Segment D7 Retention
    if 'segment' in results:
        segment_retention = results['segment']['segment_retention']
        clusters = [str(s['cluster_id']) for s in segment_retention]
        d7_rates = [s['d7_retention_rate'] for s in segment_retention]
        
        fig.add_trace(
            go.Bar(x=clusters, y=d7_rates, name='D7 리텐션',
                  marker_color='#FFA15A',
                  text=[f"{rate:.1f}%" for rate in d7_rates],
                  textposition='outside'),
            row=2, col=2
        )
        
        # 5. Segment Distribution
        segment_stats = results['segment']['segment_statistics']
        labels = [f"클러스터 {s['cluster_id']}" for s in segment_stats]
        values = [s['size'] for s in segment_stats]
        
        fig.add_trace(
            go.Pie(labels=labels, values=values, name='세그먼트',
                  marker_colors=['#636EFA', '#EF553B', '#00CC96']),
            row=3, col=1
        )
        
        # 6. HTE Analysis
        if results['segment'].get('heterogeneous_treatment_effects'):
            hte_data = results['segment']['heterogeneous_treatment_effects']
            clusters = [str(h['cluster_id']) for h in hte_data]
            control = [h['control_conversion_rate'] for h in hte_data]
            treatment = [h['treatment_conversion_rate'] for h in hte_data]
            
            fig.add_trace(
                go.Bar(x=clusters, y=control, name='대조군',
                      marker_color='#636EFA'),
                row=3, col=2
            )
            fig.add_trace(
                go.Bar(x=clusters, y=treatment, name='실험군',
                      marker_color='#EF553B'),
                row=3, col=2
            )
    
    # Update layout
    fig.update_layout(
        title_text="<b>데이터 분석 대시보드</b><br><sub>리텐션, A/B 테스트, 사용자 세그먼테이션 분석</sub>",
        title_font_size=24,
        showlegend=True,
        height=1400,
        template="plotly_white"
    )
    
    # Update axes
    fig.update_xaxes(title_text="일자", row=1, col=1)
    fig.update_yaxes(title_text="리텐션율 (%)", row=1, col=1)
    fig.update_xaxes(title_text="일자", row=1, col=2)
    fig.update_yaxes(title_text="리텐션율 (%)", row=1, col=2)
    fig.update_yaxes(title_text="전환율 (%)", row=2, col=1)
    fig.update_xaxes(title_text="클러스터", row=2, col=2)
    fig.update_yaxes(title_text="D7 리텐션 (%)", row=2, col=2)
    fig.update_xaxes(title_text="클러스터", row=3, col=2)
    fig.update_yaxes(title_text="전환율 (%)", row=3, col=2)
    
    # Create HTML with custom styling
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>데이터 분석 대시보드 - apply-demo-2</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
            font-size: 18px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .metric-label {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 8px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
        }}
        .chart-container {{
            margin-top: 30px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 데이터 분석 대시보드</h1>
        <div class="subtitle">리텐션, A/B 테스트, 사용자 세그먼테이션 종합 분석</div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">D7 리텐션</div>
                <div class="metric-value">{results['retention']['overall_retention']['D7']['retention_rate']}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">대조군 전환율</div>
                <div class="metric-value">{results['ab_test']['group_a']['conversion_rate_pct']}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">실험군 전환율</div>
                <div class="metric-value">{results['ab_test']['group_b']['conversion_rate_pct']}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">사용자 세그먼트</div>
                <div class="metric-value">{results['segment']['n_clusters']}개</div>
            </div>
        </div>
        
        <div class="chart-container">
            {fig.to_html(include_plotlyjs='cdn', div_id='dashboard')}
        </div>
        
        <div class="footer">
            <p><strong>데이터 분석 프로젝트</strong> | 
            <a href="https://github.com/baobabkim/apply-demo-2" target="_blank">GitHub 리포지토리</a> | 
            Made with ❤️ by baobabkim</p>
            <p style="font-size: 12px; margin-top: 10px;">
                마지막 업데이트: {results['retention']['analysis_timestamp'][:10]}
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    output_path = "docs/index.html"
    Path("docs").mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[OK] 정적 대시보드 생성 완료: {output_path}")
    print(f"[INFO] 파일 크기: {len(html_content) / 1024:.1f} KB")
    print(f"\n로컬에서 확인: file:///{Path(output_path).absolute()}")


if __name__ == "__main__":
    create_static_dashboard()
