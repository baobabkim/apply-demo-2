"""
User generation script for creating synthetic user data.

This module generates 10,000+ virtual users with realistic signup patterns,
channel distribution, and initial segmentation.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Tuple


def generate_users(
    db_path: str = "data/app_data.db",
    num_users: int = 10000,
    days_back: int = 60
) -> None:
    """
    Generate synthetic user data and insert into database.
    
    Args:
        db_path: Path to the SQLite database
        num_users: Number of users to generate
        days_back: Number of days back from today for signup distribution
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Channel distribution: organic 50%, paid 30%, referral 20%
    channels = ['organic', 'paid', 'referral']
    channel_weights = [0.5, 0.3, 0.2]
    
    # Segment distribution (initial classification)
    segments = ['high_potential', 'medium_potential', 'low_potential']
    segment_weights = [0.3, 0.5, 0.2]
    
    users_data: List[Tuple] = []
    
    # Generate signup dates with realistic distribution
    # More signups in recent days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"Generating {num_users} users...")
    
    for user_id in range(1, num_users + 1):
        # Generate signup date with bias towards recent dates
        # Use beta distribution for realistic pattern
        days_offset = int(random.betavariate(2, 5) * days_back)
        signup_date = (end_date - timedelta(days=days_offset)).strftime('%Y-%m-%d')
        
        # Select channel based on weights
        channel = random.choices(channels, weights=channel_weights)[0]
        
        # Select initial segment based on weights
        segment = random.choices(segments, weights=segment_weights)[0]
        
        users_data.append((user_id, signup_date, channel, segment))
        
        # Progress indicator
        if user_id % 1000 == 0:
            print(f"  Generated {user_id}/{num_users} users...")
    
    # Insert users into database
    cursor.executemany(
        "INSERT INTO users (user_id, signup_date, channel, segment) VALUES (?, ?, ?, ?)",
        users_data
    )
    
    conn.commit()
    conn.close()
    
    print(f"[OK] Successfully generated and inserted {num_users} users")
    print(f"  Signup date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"  Channel distribution: organic={channel_weights[0]*100}%, paid={channel_weights[1]*100}%, referral={channel_weights[2]*100}%")
    print(f"  Segment distribution: high={segment_weights[0]*100}%, medium={segment_weights[1]*100}%, low={segment_weights[2]*100}%")


if __name__ == "__main__":
    generate_users()
