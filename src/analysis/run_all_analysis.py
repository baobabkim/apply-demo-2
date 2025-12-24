"""
Main analysis pipeline.

This script runs all analysis modules in sequence and generates a comprehensive report.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.retention_analysis import calculate_retention
from analysis.ab_test_analysis import analyze_ab_test
from analysis.segment_analysis import analyze_segments


def run_all_analysis(db_path: str = "data/app_data.db") -> None:
    """
    Run complete analysis pipeline.
    
    Args:
        db_path: Path to the SQLite database
    """
    print("=" * 60)
    print("DATA ANALYSIS PIPELINE")
    print("=" * 60)
    print()
    
    start_time = time.time()
    
    # Step 1: Retention analysis
    print("[1/3] Running retention analysis...")
    print("-" * 60)
    retention_results = calculate_retention(db_path)
    print()
    
    # Step 2: A/B test analysis
    print("[2/3] Running A/B test analysis...")
    print("-" * 60)
    ab_test_results = analyze_ab_test(db_path)
    print()
    
    # Step 3: Segment analysis
    print("[3/3] Running segment analysis...")
    print("-" * 60)
    segment_results = analyze_segments(db_path, n_clusters=3)
    print()
    
    elapsed_time = time.time() - start_time
    
    # Generate summary report
    print("=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print()
    
    print("RETENTION METRICS:")
    for day, metrics in retention_results['overall_retention'].items():
        print(f"  {day}: {metrics['retention_rate']}% ({metrics['retained_users']}/{metrics['total_users']})")
    print()
    
    print("A/B TEST RESULTS:")
    print(f"  Control (A): {ab_test_results['group_a']['conversion_rate_pct']}%")
    print(f"  Treatment (B): {ab_test_results['group_b']['conversion_rate_pct']}%")
    print(f"  Lift: {ab_test_results['effect_size']['relative_lift_pct']}%")
    print(f"  P-value: {ab_test_results['statistical_tests']['z_test']['p_value']}")
    print(f"  Significant: {ab_test_results['statistical_tests']['z_test']['significant']}")
    print(f"  Recommendation: {ab_test_results['recommendation']}")
    print()
    
    print("USER SEGMENTS:")
    for segment in segment_results['segment_statistics']:
        print(f"  Cluster {segment['cluster_id']}: {segment['size']} users ({segment['percentage']}%)")
        print(f"    Avg events: {segment['avg_total_events']}, Avg rewards: {segment['avg_reward_count']}")
    print()
    
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Total time: {elapsed_time:.2f} seconds")
    print()
    print("Results saved to:")
    print("  - data/analysis_results/retention_analysis.json")
    print("  - data/analysis_results/ab_test_analysis.json")
    print("  - data/analysis_results/segment_analysis.json")
    print()
    print("Next step:")
    print("  Launch dashboard: streamlit run src/dashboard/app.py")


if __name__ == "__main__":
    run_all_analysis()
