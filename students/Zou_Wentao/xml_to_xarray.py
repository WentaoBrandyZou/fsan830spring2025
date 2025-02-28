"""
Script for converting XML race results to xarray dataset.
"""

import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import xarray as xr
import os

def parse_xml_to_xarray(xml_path):
    """
    Parse XML race results file into xarray Dataset.
    
    Args:
        xml_path (str): Path to XML file
        
    Returns:
        xr.Dataset: Dataset containing race information
    """
    # Parse XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Extract track info
    track_elem = root.find('TRACK')
    track_id = track_elem.find('CODE').text
    track_name = track_elem.find('NAME').text
    race_date = root.get('RACE_DATE')
    
    # Process all races
    all_entries = []
    
    # Find all RACE elements
    for race in root.findall('RACE'):
        race_number = int(race.get('NUMBER'))
        race_purse = float(race.find('PURSE').text)
        race_distance = float(race.find('DISTANCE').text)
        track_condition = race.find('TRK_COND').text
        
        # Process entries for this race
        for entry in race.findall('ENTRY'):
            # Get horse name
            horse_name = entry.find('NAME').text
            
            # Get jockey info
            jockey_elem = entry.find('JOCKEY')
            jockey_name_parts = [
                jockey_elem.find('FIRST_NAME').text or '',
                jockey_elem.find('MIDDLE_NAME').text or '',
                jockey_elem.find('LAST_NAME').text or ''
            ]
            jockey_name = ' '.join(part for part in jockey_name_parts if part).strip()
            
            # Get trainer info
            trainer_elem = entry.find('TRAINER')
            trainer_name_parts = [
                trainer_elem.find('FIRST_NAME').text or '',
                trainer_elem.find('MIDDLE_NAME').text or '',
                trainer_elem.find('LAST_NAME').text or ''
            ]
            trainer_name = ' '.join(part for part in trainer_name_parts if part).strip()
            
            # Get finish position and odds
            finish_pos = int(entry.find('OFFICIAL_FIN').text)
            odds = float(entry.find('DOLLAR_ODDS').text)
            
            all_entries.append({
                'race_number': race_number,
                'horse': horse_name,
                'jockey': jockey_name,
                'trainer': trainer_name,
                'finish_position': finish_pos,
                'odds': odds,
                'purse': race_purse,
                'distance': race_distance,
                'track_condition': track_condition
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(all_entries)
    
    # Create xarray Dataset
    ds = xr.Dataset(
        data_vars={
            'finish_position': ('entry', df['finish_position'].values),
            'odds': ('entry', df['odds'].values),
            'jockey': ('entry', df['jockey'].values),
            'trainer': ('entry', df['trainer'].values),
            'race_number': ('entry', df['race_number'].values),
            'purse': ('entry', df['purse'].values),
            'distance': ('entry', df['distance'].values),
            'track_condition': ('entry', df['track_condition'].values)
        },
        coords={
            'entry': ('entry', df['horse'].values),
            'track_id': track_id,
            'track_name': track_name,
            'race_date': race_date
        }
    )
    
    return ds

def main():
    # Path to XML file
    xml_path = "data/sampleRaceResults/del20230708tch.xml"
    
    # Parse XML to xarray Dataset
    ds = parse_xml_to_xarray(xml_path)
    
    # save xarray dataset to netcdf file
    ds.to_netcdf("data/sampleRaceResults/del20230708tch.nc")

if __name__ == "__main__":
    main() 
