"""
A/B test data generation script.

This module assigns users to A/B test groups and generates conversion data
with realistic conversion rates showing treatment effect.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Tuple


def generate_ab_test(
    db_path: str = "data/app_data.db",
    control_conversion_rate: float = 0.175,
    treatment_lift: float = 0.12
) -> None:
    """
    Generate A/B test data with group assignment and conversions.
    
    Args:
        db_path: Path to the SQLite database
        control_conversion_rate: Baseline conversion rate for control group (A)
        treatment_lift: Relative lift for treatment group (B) - e.g., 0.12 = 12% increase
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch all users
    cursor.execute("SELECT user_id, signup_date FROM users")
    users = cursor.fetchall()
    
    print(f"Generating A/B test data for {len(users)} users...")
    
    # Calculate treatment conversion rate
    treatment_conversion_rate = control_conversion_rate * (1 + treatment_lift)
    
    ab_test_data: List[Tuple] = []
    
    # Randomly assign users to groups (50:50 split)
    random.shuffle(users)
    midpoint = len(users) // 2
    
    control_group = users[:midpoint]
    treatment_group = users[midpoint:]
    
    control_conversions = 0
    treatment_conversions = 0
    
    # Process control group (A)
    for user_id, signup_date_str in control_group:
        is_converted = 1 if random.random() < control_conversion_rate else 0
        
        if is_converted:
            control_conversions += 1
            # Generate conversion timestamp (within 7 days of signup)
            signup_date = datetime.strptime(signup_date_str, '%Y-%m-%d')
            days_to_conversion = random.randint(0, 7)
            conversion_time = signup_date + timedelta(
                days=days_to_conversion,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            conversion_timestamp = conversion_time.isoformat()
        else:
            conversion_timestamp = None
        
        ab_test_data.append((user_id, 'A', is_converted, conversion_timestamp))
    
    # Process treatment group (B)
    for user_id, signup_date_str in treatment_group:
        is_converted = 1 if random.random() < treatment_conversion_rate else 0
        
        if is_converted:
            treatment_conversions += 1
            # Generate conversion timestamp (within 7 days of signup)
            signup_date = datetime.strptime(signup_date_str, '%Y-%m-%d')
            days_to_conversion = random.randint(0, 7)
            conversion_time = signup_date + timedelta(
                days=days_to_conversion,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            conversion_timestamp = conversion_time.isoformat()
        else:
            conversion_timestamp = None
        
        ab_test_data.append((user_id, 'B', is_converted, conversion_timestamp))
    
    # Insert A/B test data into database
    cursor.executemany(
        "INSERT INTO ab_test_results (user_id, group_name, is_converted, conversion_timestamp) VALUES (?, ?, ?, ?)",
        ab_test_data
    )
    
    conn.commit()
    conn.close()
    
    # Calculate actual rates
    actual_control_rate = control_conversions / len(control_group)
    actual_treatment_rate = treatment_conversions / len(treatment_group)
    actual_lift = (actual_treatment_rate - actual_control_rate) / actual_control_rate
    
    print(f"[OK] Successfully generated A/B test data")
    print(f"  Control group (A): {len(control_group)} users, {control_conversions} conversions ({actual_control_rate:.2%})")
    print(f"  Treatment group (B): {len(treatment_group)} users, {treatment_conversions} conversions ({actual_treatment_rate:.2%})")
    print(f"  Actual lift: {actual_lift:.2%}")
    print(f"  Expected lift: {treatment_lift:.2%}")


if __name__ == "__main__":
    generate_ab_test()
