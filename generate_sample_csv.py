"""
Script to generate a sample CSV file for backtesting.
This creates a sample_data.csv file that can be used instead of generated data.
"""

from data_loader import generate_sample_data


def create_sample_csv():
    """Create a sample CSV file with OHLC data."""
    print("Generating sample CSV data file...")
    
    # Generate sample data
    df = generate_sample_data(num_candles=5000, start_price=2000.0)
    
    # Reset index to include timestamp as column
    df_export = df.reset_index()
    
    # Save to CSV
    filename = 'sample_data.csv'
    df_export.to_csv(filename, index=False)
    
    print(f"✓ Created {filename} with {len(df)} candles")
    print(f"  Columns: {', '.join(df_export.columns)}")
    print(f"  Date range: {df.index[0]} to {df.index[-1]}")
    print("\nYou can now use this file in main.py by modifying the data loading section.")


if __name__ == "__main__":
    create_sample_csv()
