"""
Main data generation pipeline.

This script runs all data generation modules in the correct order:
1. Create database schema
2. Generate users
3. Generate behavior logs
4. Generate A/B test data
"""

import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_generation.create_db import create_database
from data_generation.generate_users import generate_users
from data_generation.generate_logs import generate_logs
from data_generation.generate_ab_test import generate_ab_test


def run_all_generation(db_path: str = "data/app_data.db") -> None:
    """
    Run complete data generation pipeline.
    
    Args:
        db_path: Path to the SQLite database
    """
    print("=" * 60)
    print("DATA GENERATION PIPELINE")
    print("=" * 60)
    print()
    
    start_time = time.time()
    
    # Step 1: Create database
    print("[1/4] Creating database schema...")
    create_database(db_path)
    print()
    
    # Step 2: Generate users
    print("[2/4] Generating user data...")
    generate_users(db_path, num_users=10000, days_back=60)
    print()
    
    # Step 3: Generate behavior logs
    print("[3/4] Generating behavior logs...")
    generate_logs(db_path, days_to_simulate=60)
    print()
    
    # Step 4: Generate A/B test data
    print("[4/4] Generating A/B test data...")
    generate_ab_test(db_path, control_conversion_rate=0.175, treatment_lift=0.12)
    print()
    
    elapsed_time = time.time() - start_time
    
    print("=" * 60)
    print("DATA GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total time: {elapsed_time:.2f} seconds")
    print(f"Database location: {db_path}")
    print()
    print("Next steps:")
    print("  1. Run analysis: python src/analysis/run_all_analysis.py")
    print("  2. Launch dashboard: streamlit run src/dashboard/app.py")


if __name__ == "__main__":
    run_all_generation()
