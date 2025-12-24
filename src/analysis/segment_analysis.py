"""
User segmentation analysis module.

This module performs K-means clustering on user behavior features and analyzes
segment characteristics, retention, and heterogeneous treatment effects.
"""

import sqlite3
import json
from typing import Dict, List
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from datetime import datetime


def analyze_segments(
    db_path: str = "data/app_data.db",
    output_path: str = "data/analysis_results/segment_analysis.json",
    n_clusters: int = 3
) -> Dict:
    """
    Perform user segmentation using K-means clustering and analyze segments.
    
    Args:
        db_path: Path to the SQLite database
        output_path: Path to save analysis results
        n_clusters: Number of clusters for K-means
        
    Returns:
        Dictionary containing segmentation analysis results
    """
    conn = sqlite3.connect(db_path)
    
    print("Extracting user behavior features...")
    
    # Feature engineering query
    query = """
    WITH user_features AS (
        SELECT 
            u.user_id,
            u.signup_date,
            u.channel,
            u.segment as initial_segment,
            COUNT(ul.log_id) as total_events,
            COUNT(DISTINCT DATE(ul.event_timestamp)) as active_days,
            JULIANDAY('now') - JULIANDAY(u.signup_date) as days_since_signup,
            SUM(CASE WHEN ul.event_name = 'reward_earned' THEN 1 ELSE 0 END) as reward_count,
            SUM(CASE WHEN ul.event_name = 'reward_earned' THEN ul.value ELSE 0 END) as total_reward_value,
            SUM(CASE WHEN ul.event_name = 'activity_completed' THEN 1 ELSE 0 END) as activities_completed,
            MIN(CASE WHEN ul.event_name = 'reward_earned' 
                THEN JULIANDAY(ul.event_timestamp) - JULIANDAY(u.signup_date) 
                ELSE NULL END) as days_to_first_reward
        FROM users u
        LEFT JOIN user_logs ul ON u.user_id = ul.user_id
        GROUP BY u.user_id
    )
    SELECT 
        *,
        CASE WHEN days_since_signup > 0 
            THEN CAST(total_events AS FLOAT) / days_since_signup 
            ELSE 0 END as avg_daily_events,
        CASE WHEN days_since_signup > 0 
            THEN CAST(active_days AS FLOAT) / days_since_signup 
            ELSE 0 END as activity_ratio
    FROM user_features
    """
    
    df = pd.read_sql_query(query, conn)
    
    print(f"  Extracted features for {len(df)} users")
    
    # Select features for clustering
    feature_cols = [
        'total_events',
        'active_days', 
        'reward_count',
        'total_reward_value',
        'activities_completed',
        'avg_daily_events',
        'activity_ratio'
    ]
    
    # Fill NaN values
    df[feature_cols] = df[feature_cols].fillna(0)
    
    X = df[feature_cols].values
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Determine optimal number of clusters using Elbow Method
    print("\nDetermining optimal number of clusters...")
    inertias = []
    silhouette_scores = []
    K_range = range(2, 8)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))
    
    elbow_data = [
        {'k': k, 'inertia': inertia, 'silhouette_score': score}
        for k, inertia, score in zip(K_range, inertias, silhouette_scores)
    ]
    
    print("  K | Inertia | Silhouette")
    for item in elbow_data:
        print(f"  {item['k']} | {item['inertia']:.2f} | {item['silhouette_score']:.4f}")
    
    # Perform K-means with specified number of clusters
    print(f"\nPerforming K-means clustering with {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Analyze segment characteristics
    print("\nAnalyzing segment characteristics...")
    segment_stats = []
    
    for cluster_id in range(n_clusters):
        cluster_df = df[df['cluster'] == cluster_id]
        
        stats = {
            'cluster_id': int(cluster_id),
            'size': len(cluster_df),
            'percentage': round(len(cluster_df) / len(df) * 100, 2),
            'avg_total_events': round(cluster_df['total_events'].mean(), 2),
            'avg_active_days': round(cluster_df['active_days'].mean(), 2),
            'avg_reward_count': round(cluster_df['reward_count'].mean(), 2),
            'avg_reward_value': round(cluster_df['total_reward_value'].mean(), 2),
            'avg_activities': round(cluster_df['activities_completed'].mean(), 2),
            'avg_daily_events': round(cluster_df['avg_daily_events'].mean(), 2)
        }
        
        segment_stats.append(stats)
        
        print(f"\n  Cluster {cluster_id}: {stats['size']} users ({stats['percentage']}%)")
        print(f"    Avg events: {stats['avg_total_events']}")
        print(f"    Avg active days: {stats['avg_active_days']}")
        print(f"    Avg rewards: {stats['avg_reward_count']}")
    
    # Segment-specific retention (D7)
    print("\nCalculating segment-specific D7 retention...")
    
    # Save cluster assignments to database temporarily
    df[['user_id', 'cluster']].to_sql('temp_clusters', conn, if_exists='replace', index=False)
    
    retention_query = """
    WITH user_activity AS (
        SELECT DISTINCT 
            ul.user_id,
            DATE(ul.event_timestamp) as activity_date
        FROM user_logs ul
    )
    SELECT 
        tc.cluster,
        COUNT(DISTINCT u.user_id) as total_users,
        COUNT(DISTINCT CASE 
            WHEN DATE(ua.activity_date) = DATE(u.signup_date, '+7 days')
            THEN u.user_id 
        END) as d7_retained
    FROM users u
    JOIN temp_clusters tc ON u.user_id = tc.user_id
    LEFT JOIN user_activity ua ON u.user_id = ua.user_id
    WHERE DATE(u.signup_date, '+7 days') <= DATE('now')
    GROUP BY tc.cluster
    """
    
    retention_df = pd.read_sql_query(retention_query, conn)
    
    segment_retention = []
    for _, row in retention_df.iterrows():
        retention_rate = (row['d7_retained'] / row['total_users'] * 100) if row['total_users'] > 0 else 0
        segment_retention.append({
            'cluster_id': int(row['cluster']),
            'total_users': int(row['total_users']),
            'd7_retained': int(row['d7_retained']),
            'd7_retention_rate': round(retention_rate, 2)
        })
        print(f"  Cluster {row['cluster']}: D7 retention = {retention_rate:.2f}%")
    
    # Heterogeneous Treatment Effect (HTE) analysis
    print("\nAnalyzing heterogeneous treatment effects...")
    
    hte_query = """
    SELECT 
        tc.cluster,
        ab.group_name,
        COUNT(*) as total_users,
        SUM(ab.is_converted) as conversions
    FROM ab_test_results ab
    JOIN temp_clusters tc ON ab.user_id = tc.user_id
    GROUP BY tc.cluster, ab.group_name
    """
    
    hte_df = pd.read_sql_query(hte_query, conn)
    
    hte_analysis = []
    for cluster_id in range(n_clusters):
        cluster_data = hte_df[hte_df['cluster'] == cluster_id]
        
        if len(cluster_data) == 2:
            group_a = cluster_data[cluster_data['group_name'] == 'A'].iloc[0]
            group_b = cluster_data[cluster_data['group_name'] == 'B'].iloc[0]
            
            conv_rate_a = group_a['conversions'] / group_a['total_users']
            conv_rate_b = group_b['conversions'] / group_b['total_users']
            lift = ((conv_rate_b - conv_rate_a) / conv_rate_a * 100) if conv_rate_a > 0 else 0
            
            hte_analysis.append({
                'cluster_id': int(cluster_id),
                'control_conversion_rate': round(conv_rate_a * 100, 2),
                'treatment_conversion_rate': round(conv_rate_b * 100, 2),
                'lift_pct': round(lift, 2)
            })
            
            print(f"  Cluster {cluster_id}: Control={conv_rate_a*100:.2f}%, Treatment={conv_rate_b*100:.2f}%, Lift={lift:.2f}%")
    
    # Clean up temp table
    conn.execute("DROP TABLE IF EXISTS temp_clusters")
    conn.close()
    
    # Compile results
    results = {
        'n_clusters': n_clusters,
        'total_users': len(df),
        'elbow_analysis': elbow_data,
        'segment_statistics': segment_stats,
        'segment_retention': segment_retention,
        'heterogeneous_treatment_effects': hte_analysis,
        'feature_importance': {
            'features_used': feature_cols,
            'scaler_mean': scaler.mean_.tolist(),
            'scaler_std': scaler.scale_.tolist()
        },
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    # Save results
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[OK] Segment analysis complete. Results saved to {output_path}")
    
    return results


if __name__ == "__main__":
    analyze_segments()
