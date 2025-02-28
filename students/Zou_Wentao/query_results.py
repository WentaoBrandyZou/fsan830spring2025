"""
Script for querying race results from xarray dataset.
"""

import xarray as xr
import pandas as pd
import numpy as np

def get_top_three_finishers(ds):
    """
    Get the top 3 finishers from each race with their details.
    
    Args:
        ds (xr.Dataset): Dataset containing race information
        
    Returns:
        pd.DataFrame: DataFrame with top 3 finishers and their details
    """
    results_list = []
    
    # Get unique race numbers
    race_numbers = np.unique(ds.race_number.values)
    
    # Process each race separately
    for race_num in race_numbers:
        # Get entries for this race
        race_entries = ds.where(ds.race_number == race_num, drop=True)
        
        # Get indices of top 3 finishers in this race
        top_three_indices = np.argsort(race_entries.finish_position.values)[:3]
        
        # Extract data for top 3 finishers
        for idx in top_three_indices:
            results_list.append({
                'Horse': race_entries.entry.values[idx],
                'Jockey': race_entries.jockey.values[idx],
                'Trainer': race_entries.trainer.values[idx],
                'Position': race_entries.finish_position.values[idx],
                'Odds': race_entries.odds.values[idx],
                'Race Number': race_num,
                'Track': f"{race_entries.track_name.item()} ({race_entries.track_id.item()})",
                'Date': race_entries.race_date.item()
            })
    
    # Convert to DataFrame
    results = pd.DataFrame(results_list)
    
    # Sort by race number and finishing position
    results = results.sort_values(['Race Number', 'Position'])
    
    return results

def main():
    # Load the dataset
    ds = xr.open_dataset("data/sampleRaceResults/del20230708tch.nc")
    
    # Get top 3 finishers
    top_three_results = get_top_three_finishers(ds)
    
    # Print results in a formatted way
    print("\nTop 3 Finishers for Each Race:")
    print("=" * 80)
    
    for race_num in top_three_results['Race Number'].unique():
        race_results = top_three_results[top_three_results['Race Number'] == race_num]
        
        print(f"\nRace {race_num}")
        print("-" * 80)
        for _, row in race_results.iterrows():
            print(f"Position: {row['Position']}")
            print(f"Horse: {row['Horse']}")
            print(f"Jockey: {row['Jockey']}")
            print(f"Trainer: {row['Trainer']}")
            print(f"Odds: {row['Odds']:.1f}")
            print("-" * 40)
    
    print(f"\nTrack: {race_results['Track'].iloc[0]}")
    print(f"Date: {race_results['Date']}")

if __name__ == "__main__":
    main()
