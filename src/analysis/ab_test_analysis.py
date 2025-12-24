"""
A/B test statistical analysis module.

This module performs comprehensive statistical testing on A/B test results including
two-proportion z-test, chi-square test, effect size calculation, and power analysis.
"""

import sqlite3
import json
import math
from typing import Dict
import pandas as pd
from scipy import stats
import numpy as np


def analyze_ab_test(
    db_path: str = "data/app_data.db",
    output_path: str = "data/analysis_results/ab_test_analysis.json"
) -> Dict:
    """
    Perform statistical analysis on A/B test results.
    
    Args:
        db_path: Path to the SQLite database
        output_path: Path to save analysis results
        
    Returns:
        Dictionary containing A/B test analysis results
    """
    conn = sqlite3.connect(db_path)
    
    print("Analyzing A/B test results...")
    
    # Get conversion data
    query = """
    SELECT 
        group_name,
        COUNT(*) as total_users,
        SUM(is_converted) as conversions
    FROM ab_test_results
    GROUP BY group_name
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Extract data for both groups
    group_a = df[df['group_name'] == 'A'].iloc[0]
    group_b = df[df['group_name'] == 'B'].iloc[0]
    
    n_a = group_a['total_users']
    n_b = group_b['total_users']
    conv_a = group_a['conversions']
    conv_b = group_b['conversions']
    
    p_a = conv_a / n_a
    p_b = conv_b / n_b
    
    print(f"  Control (A): {conv_a}/{n_a} = {p_a:.4f} ({p_a*100:.2f}%)")
    print(f"  Treatment (B): {conv_b}/{n_b} = {p_b:.4f} ({p_b*100:.2f}%)")
    
    # Calculate pooled proportion for z-test
    p_pool = (conv_a + conv_b) / (n_a + n_b)
    se_pool = math.sqrt(p_pool * (1 - p_pool) * (1/n_a + 1/n_b))
    
    # Two-proportion z-test
    z_score = (p_b - p_a) / se_pool if se_pool > 0 else 0
    p_value_z = 2 * (1 - stats.norm.cdf(abs(z_score)))  # Two-tailed
    
    print(f"\nTwo-proportion z-test:")
    print(f"  Z-score: {z_score:.4f}")
    print(f"  P-value: {p_value_z:.4f}")
    
    # Chi-square test
    contingency_table = [[conv_a, n_a - conv_a], [conv_b, n_b - conv_b]]
    chi2, p_value_chi2, dof, expected = stats.chi2_contingency(contingency_table)
    
    print(f"\nChi-square test:")
    print(f"  Chi-square: {chi2:.4f}")
    print(f"  P-value: {p_value_chi2:.4f}")
    
    # Effect size (Cohen's h)
    phi_a = 2 * math.asin(math.sqrt(p_a))
    phi_b = 2 * math.asin(math.sqrt(p_b))
    cohens_h = phi_b - phi_a
    
    print(f"\nEffect size (Cohen's h): {cohens_h:.4f}")
    
    # Relative lift
    relative_lift = ((p_b - p_a) / p_a * 100) if p_a > 0 else 0
    absolute_lift = (p_b - p_a) * 100
    
    print(f"Relative lift: {relative_lift:.2f}%")
    print(f"Absolute lift: {absolute_lift:.2f} percentage points")
    
    # 95% Confidence interval for difference
    se_diff = math.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    ci_lower = (p_b - p_a) - 1.96 * se_diff
    ci_upper = (p_b - p_a) + 1.96 * se_diff
    
    print(f"\n95% CI for difference: [{ci_lower*100:.2f}%, {ci_upper*100:.2f}%]")
    
    # Statistical power calculation (post-hoc)
    # Using normal approximation
    effect_size = abs(p_b - p_a)
    pooled_p = (n_a * p_a + n_b * p_b) / (n_a + n_b)
    pooled_se = math.sqrt(pooled_p * (1 - pooled_p) * (1/n_a + 1/n_b))
    
    # Calculate non-centrality parameter
    ncp = effect_size / pooled_se if pooled_se > 0 else 0
    
    # Power = P(reject H0 | H1 is true)
    critical_value = 1.96  # For alpha = 0.05, two-tailed
    power = 1 - stats.norm.cdf(critical_value - ncp) + stats.norm.cdf(-critical_value - ncp)
    
    print(f"Statistical power: {power:.4f} ({power*100:.2f}%)")
    
    # Compile results
    results = {
        'group_a': {
            'total_users': int(n_a),
            'conversions': int(conv_a),
            'conversion_rate': round(p_a, 4),
            'conversion_rate_pct': round(p_a * 100, 2)
        },
        'group_b': {
            'total_users': int(n_b),
            'conversions': int(conv_b),
            'conversion_rate': round(p_b, 4),
            'conversion_rate_pct': round(p_b * 100, 2)
        },
        'statistical_tests': {
            'z_test': {
                'z_score': round(float(z_score), 4),
                'p_value': round(float(p_value_z), 4),
                'significant': bool(p_value_z < 0.05)
            },
            'chi_square_test': {
                'chi_square': round(float(chi2), 4),
                'p_value': round(float(p_value_chi2), 4),
                'degrees_of_freedom': int(dof),
                'significant': bool(p_value_chi2 < 0.05)
            }
        },
        'effect_size': {
            'cohens_h': round(cohens_h, 4),
            'relative_lift_pct': round(relative_lift, 2),
            'absolute_lift_pct': round(absolute_lift, 2)
        },
        'confidence_interval_95': {
            'lower': round(ci_lower * 100, 2),
            'upper': round(ci_upper * 100, 2)
        },
        'statistical_power': round(power, 4),
        'recommendation': 'Deploy treatment' if (p_value_z < 0.05 and p_b > p_a) else 'Keep control or run longer test',
        'analysis_timestamp': pd.Timestamp.now().isoformat()
    }
    
    # Save results
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[OK] A/B test analysis complete. Results saved to {output_path}")
    print(f"Recommendation: {results['recommendation']}")
    
    return results


if __name__ == "__main__":
    analyze_ab_test()
