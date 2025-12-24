"""
Retention analysis module.

This module calculates retention metrics including D1, D3, D7, D14, D30 retention,
cohort analysis, and comparison between reward-earning and non-reward users.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
from scipy import stats


def calculate_retention(
    db_path: str = "data/app_data.db",
    output_path: str = "data/analysis_results/retention_analysis.json"
) -> Dict:
    """
    Calculate retention metrics and perform cohort analysis.
    
    Args:
        db_path: Path to the SQLite database
        output_path: Path to save analysis results
        
    Returns:
        Dictionary containing retention analysis results
    """
    conn = sqlite3.connect(db_path)
    
    print("Calculating retention metrics...")
    
    # Calculate overall retention rates
    retention_days = [1, 3, 7, 14, 30]
    overall_retention = {}
    
    for day in retention_days:
        query = f"""
        WITH user_signup AS (
            SELECT user_id, signup_date
            FROM users
        ),
        user_activity AS (
            SELECT DISTINCT 
                ul.user_id,
                DATE(ul.event_timestamp) as activity_date
            FROM user_logs ul
        )
        SELECT 
            COUNT(DISTINCT us.user_id) as total_users,
            COUNT(DISTINCT CASE 
                WHEN DATE(ua.activity_date) = DATE(us.signup_date, '+{day} days')
                THEN us.user_id 
            END) as retained_users
        FROM user_signup us
        LEFT JOIN user_activity ua ON us.user_id = ua.user_id
        WHERE DATE(us.signup_date, '+{day} days') <= DATE('now')
        """
        
        df = pd.read_sql_query(query, conn)
        total = df['total_users'].iloc[0]
        retained = df['retained_users'].iloc[0]
        retention_rate = (retained / total * 100) if total > 0 else 0
        
        overall_retention[f'D{day}'] = {
            'total_users': int(total),
            'retained_users': int(retained),
            'retention_rate': round(retention_rate, 2)
        }
        print(f"  D{day} retention: {retention_rate:.2f}% ({retained}/{total})")
    
    # Compare reward vs non-reward users
    print("\nComparing reward-earning vs non-reward users...")
    
    reward_comparison = {}
    for day in retention_days:
        query = f"""
        WITH user_signup AS (
            SELECT user_id, signup_date
            FROM users
        ),
        reward_users AS (
            SELECT DISTINCT user_id
            FROM user_logs
            WHERE event_name = 'reward_earned'
            AND DATE(event_timestamp) = DATE((SELECT signup_date FROM users WHERE users.user_id = user_logs.user_id))
        ),
        user_activity AS (
            SELECT DISTINCT 
                ul.user_id,
                DATE(ul.event_timestamp) as activity_date
            FROM user_logs ul
        )
        SELECT 
            CASE WHEN ru.user_id IS NOT NULL THEN 'reward' ELSE 'no_reward' END as user_type,
            COUNT(DISTINCT us.user_id) as total_users,
            COUNT(DISTINCT CASE 
                WHEN DATE(ua.activity_date) = DATE(us.signup_date, '+{day} days')
                THEN us.user_id 
            END) as retained_users
        FROM user_signup us
        LEFT JOIN reward_users ru ON us.user_id = ru.user_id
        LEFT JOIN user_activity ua ON us.user_id = ua.user_id
        WHERE DATE(us.signup_date, '+{day} days') <= DATE('now')
        GROUP BY user_type
        """
        
        df = pd.read_sql_query(query, conn)
        
        comparison = {}
        for _, row in df.iterrows():
            user_type = row['user_type']
            total = row['total_users']
            retained = row['retained_users']
            retention_rate = (retained / total * 100) if total > 0 else 0
            
            comparison[user_type] = {
                'total_users': int(total),
                'retained_users': int(retained),
                'retention_rate': round(retention_rate, 2)
            }
        
        # Calculate statistical significance
        if 'reward' in comparison and 'no_reward' in comparison:
            contingency_table = [
                [comparison['reward']['retained_users'], 
                 comparison['reward']['total_users'] - comparison['reward']['retained_users']],
                [comparison['no_reward']['retained_users'], 
                 comparison['no_reward']['total_users'] - comparison['no_reward']['retained_users']]
            ]
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
            comparison['statistical_test'] = {
                'chi2': round(float(chi2), 4),
                'p_value': round(float(p_value), 4),
                'significant': bool(p_value < 0.05)
            }
            
            print(f"  D{day}: Reward={comparison['reward']['retention_rate']:.2f}%, No Reward={comparison['no_reward']['retention_rate']:.2f}%, p-value={p_value:.4f}")
        
        reward_comparison[f'D{day}'] = comparison
    
    # Cohort analysis
    print("\nPerforming cohort analysis...")
    cohort_query = """
    WITH user_cohorts AS (
        SELECT 
            user_id,
            DATE(signup_date, 'start of week') as cohort_week,
            signup_date
        FROM users
    ),
    user_activity AS (
        SELECT DISTINCT 
            user_id,
            DATE(event_timestamp) as activity_date
        FROM user_logs
    )
    SELECT 
        uc.cohort_week,
        COUNT(DISTINCT uc.user_id) as cohort_size,
        SUM(CASE WHEN ua.activity_date = DATE(uc.signup_date, '+1 day') THEN 1 ELSE 0 END) as d1_retained,
        SUM(CASE WHEN ua.activity_date = DATE(uc.signup_date, '+7 days') THEN 1 ELSE 0 END) as d7_retained,
        SUM(CASE WHEN ua.activity_date = DATE(uc.signup_date, '+30 days') THEN 1 ELSE 0 END) as d30_retained
    FROM user_cohorts uc
    LEFT JOIN user_activity ua ON uc.user_id = ua.user_id
    GROUP BY uc.cohort_week
    ORDER BY uc.cohort_week
    """
    
    cohort_df = pd.read_sql_query(cohort_query, conn)
    # Convert numpy types to Python types for JSON serialization
    cohort_analysis = []
    for _, row in cohort_df.iterrows():
        cohort_analysis.append({
            'cohort_week': str(row['cohort_week']),
            'cohort_size': int(row['cohort_size']),
            'd1_retained': int(row['d1_retained']),
            'd7_retained': int(row['d7_retained']),
            'd30_retained': int(row['d30_retained'])
        })
    
    conn.close()
    
    # Compile results
    results = {
        'overall_retention': overall_retention,
        'reward_comparison': reward_comparison,
        'cohort_analysis': cohort_analysis,
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    # Save results
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[OK] Retention analysis complete. Results saved to {output_path}")
    
    return results


if __name__ == "__main__":
    calculate_retention()
