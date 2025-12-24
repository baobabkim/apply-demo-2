"""
User behavior log generation script.

This module generates realistic user behavior logs including:
- app_open: App launch events
- reward_earned: Reward acquisition events
- activity_completed: Activity completion events
- app_close: App close events
"""

import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import numpy as np


def generate_logs(
    db_path: str = "data/app_data.db",
    days_to_simulate: int = 60
) -> None:
    """
    Generate synthetic user behavior logs.
    
    Args:
        db_path: Path to the SQLite database
        days_to_simulate: Number of days to simulate behavior for
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch all users
    cursor.execute("SELECT user_id, signup_date, segment FROM users")
    users = cursor.fetchall()
    
    print(f"Generating behavior logs for {len(users)} users...")
    
    # Event types
    event_types = ['app_open', 'reward_earned', 'activity_completed', 'app_close']
    
    # User behavior patterns based on segment
    behavior_patterns = {
        'high_potential': {'daily_events': (5, 10), 'reward_prob': 0.7},
        'medium_potential': {'daily_events': (2, 5), 'reward_prob': 0.4},
        'low_potential': {'daily_events': (0, 2), 'reward_prob': 0.2}
    }
    
    logs_data: List[Tuple] = []
    log_count = 0
    
    for user_id, signup_date_str, segment in users:
        signup_date = datetime.strptime(signup_date_str, '%Y-%m-%d')
        
        # Determine user's activity pattern
        pattern = behavior_patterns.get(segment, behavior_patterns['medium_potential'])
        min_events, max_events = pattern['daily_events']
        reward_prob = pattern['reward_prob']
        
        # Simulate behavior from signup date to today
        current_date = signup_date
        end_date = datetime.now()
        
        # Track if user earned reward in first 24 hours
        first_day_reward = False
        
        while current_date <= end_date:
            # Determine number of events for this day
            num_events = random.randint(min_events, max_events)
            
            for _ in range(num_events):
                # Generate event timestamp (random time during the day)
                hour = random.randint(6, 23)  # Active hours 6 AM to 11 PM
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                event_timestamp = current_date.replace(
                    hour=hour, minute=minute, second=second
                ).isoformat()
                
                # Select event type
                if not first_day_reward and (current_date - signup_date).days == 0:
                    # Higher chance of reward on first day
                    if random.random() < reward_prob * 1.5:
                        event_name = 'reward_earned'
                        first_day_reward = True
                    else:
                        event_name = random.choice(['app_open', 'activity_completed', 'app_close'])
                else:
                    # Normal event distribution
                    event_weights = [0.3, 0.1, 0.4, 0.2]  # app_open, reward, activity, app_close
                    event_name = random.choices(event_types, weights=event_weights)[0]
                
                # Generate value for reward_earned events
                value = None
                if event_name == 'reward_earned':
                    # Reward amount follows log-normal distribution
                    value = round(np.random.lognormal(mean=3.0, sigma=0.5), 2)
                
                logs_data.append((user_id, event_name, event_timestamp, value))
                log_count += 1
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Progress indicator
        if (user_id % 1000) == 0:
            print(f"  Processed {user_id}/{len(users)} users, {log_count} logs generated...")
    
    # Insert logs into database in batches
    print("Inserting logs into database...")
    batch_size = 10000
    for i in range(0, len(logs_data), batch_size):
        batch = logs_data[i:i + batch_size]
        cursor.executemany(
            "INSERT INTO user_logs (user_id, event_name, event_timestamp, value) VALUES (?, ?, ?, ?)",
            batch
        )
        conn.commit()
        print(f"  Inserted {min(i + batch_size, len(logs_data))}/{len(logs_data)} logs...")
    
    conn.close()
    
    print(f"[OK] Successfully generated and inserted {log_count} behavior logs")
    print(f"  Event types: {event_types}")
    print(f"  Behavior patterns: high_potential (5-10 events/day), medium (2-5), low (0-2)")


if __name__ == "__main__":
    generate_logs()
