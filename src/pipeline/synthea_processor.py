"""
synthea_processor.py
--------------------
Parse Synthea FHIR R4 JSON bundles and aggregate metrics to VA×month grain.

Purpose:
- Parse ~5000 FHIR Bundle JSON files (Patient, Encounter, Condition, Observation)
- Filter to Virginia patients based on birthPlace.state or address.state
- Aggregate to state_abbr='VA' × period_id=YYYYMM
- Calculate encounter counts, diagnosis rates, lab out-of-bounds rates
- Apply customer_id hashing with determinism

Outputs (columns for CohortFact_VA):
- synthea_encounters: COUNT(DISTINCT encounter_id) per VA×month
- synthea_dx_rate: (COUNT(DISTINCT condition_id) / COUNT(DISTINCT encounter_id)) × 1000 [per 1k encounters]
- synthea_lab_oob_rate: COUNT(obs where out_of_bounds=True) / COUNT(obs) [fraction 0-1]

Environment Variables:
- CAPSTONE_HMAC_SALT: Required for customer_id hashing

Usage:
    from src.pipeline.synthea_processor import process_synthea
    
    df = process_synthea(fhir_dir='data/raw/synthea/fhir')
    # Returns DataFrame with columns: state_abbr, period_id, synthea_encounters, 
    #   synthea_dx_rate, synthea_lab_oob_rate, low_precision_time, ambiguous_geo
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
from src.pipeline.customer_id_hash import hash_customer_id


# LOINC codes for common labs with known reference ranges
# Format: {loinc_code: (low, high, unit)}
LOINC_REFERENCE_RANGES = {
    # Glucose
    '2339-0': (70, 100, 'mg/dL'),      # Glucose [Mass/volume] in Blood
    '2345-7': (70, 100, 'mg/dL'),      # Glucose [Mass/volume] in Serum or Plasma
    
    # Cholesterol
    '2093-3': (0, 200, 'mg/dL'),       # Total cholesterol
    '2085-9': (40, 200, 'mg/dL'),      # HDL cholesterol
    '2089-1': (0, 100, 'mg/dL'),       # LDL cholesterol
    
    # Blood Pressure
    '8480-6': (90, 120, 'mm[Hg]'),     # Systolic BP
    '8462-4': (60, 80, 'mm[Hg]'),      # Diastolic BP
    
    # Hemoglobin A1c
    '4548-4': (0, 5.7, '%'),           # Hemoglobin A1c/Hemoglobin.total
    
    # BMI
    '39156-5': (18.5, 24.9, 'kg/m2'),  # Body mass index
}


def parse_fhir_bundle(bundle_path: Path) -> Dict:
    """
    Parse a single FHIR R4 Bundle JSON file.
    
    Args:
        bundle_path: Path to .json file containing FHIR Bundle
        
    Returns:
        Dictionary with:
        - patient_id: UUID from Patient resource
        - state: Virginia state abbreviation or None
        - encounters: List of {id, date, period_id}
        - conditions: List of {id, encounter_id, code}
        - observations: List of {id, encounter_id, code, value, unit, out_of_bounds}
    """
    with open(bundle_path, 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    
    if bundle.get('resourceType') != 'Bundle':
        raise ValueError(f"Not a FHIR Bundle: {bundle_path}")
    
    # Extract resources from bundle
    patient = None
    encounters = []
    conditions = []
    observations = []
    
    for entry in bundle.get('entry', []):
        resource = entry.get('resource', {})
        resource_type = resource.get('resourceType')
        
        if resource_type == 'Patient':
            patient = resource
        elif resource_type == 'Encounter':
            encounters.append(resource)
        elif resource_type == 'Condition':
            conditions.append(resource)
        elif resource_type == 'Observation':
            observations.append(resource)
    
    if not patient:
        return None
    
    # Extract patient ID
    patient_id = patient.get('id')
    if not patient_id:
        return None
    
    # Extract state from birthPlace or address
    state = extract_state_from_patient(patient)
    
    # Parse encounters
    encounter_list = []
    for enc in encounters:
        enc_id = enc.get('id')
        period = enc.get('period', {})
        start_date = period.get('start')
        
        if enc_id and start_date:
            try:
                dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                period_id = dt.strftime('%Y%m')  # YYYYMM format
                encounter_list.append({
                    'id': enc_id,
                    'date': start_date,
                    'period_id': period_id
                })
            except (ValueError, AttributeError):
                continue
    
    # Parse conditions (diagnoses)
    condition_list = []
    for cond in conditions:
        cond_id = cond.get('id')
        enc_ref = cond.get('encounter', {}).get('reference', '')
        enc_id = enc_ref.split('/')[-1] if enc_ref else None
        code = cond.get('code', {}).get('coding', [{}])[0].get('code')
        
        if cond_id:
            condition_list.append({
                'id': cond_id,
                'encounter_id': enc_id,
                'code': code
            })
    
    # Parse observations (labs)
    observation_list = []
    for obs in observations:
        obs_id = obs.get('id')
        enc_ref = obs.get('encounter', {}).get('reference', '')
        enc_id = enc_ref.split('/')[-1] if enc_ref else None
        
        code_obj = obs.get('code', {})
        loinc_code = None
        for coding in code_obj.get('coding', []):
            if coding.get('system') == 'http://loinc.org':
                loinc_code = coding.get('code')
                break
        
        value_qty = obs.get('valueQuantity', {})
        value = value_qty.get('value')
        unit = value_qty.get('unit')
        
        # Check if out of bounds
        out_of_bounds = False
        if loinc_code and loinc_code in LOINC_REFERENCE_RANGES and value is not None:
            low, high, ref_unit = LOINC_REFERENCE_RANGES[loinc_code]
            if unit == ref_unit:
                out_of_bounds = (value < low or value > high)
        
        if obs_id:
            observation_list.append({
                'id': obs_id,
                'encounter_id': enc_id,
                'code': loinc_code,
                'value': value,
                'unit': unit,
                'out_of_bounds': out_of_bounds
            })
    
    return {
        'patient_id': patient_id,
        'state': state,
        'encounters': encounter_list,
        'conditions': condition_list,
        'observations': observation_list
    }


def extract_state_from_patient(patient: Dict) -> Optional[str]:
    """
    Extract state abbreviation from Patient resource.
    
    Priority:
    1. birthPlace extension → state
    2. address[0] → state
    
    Returns:
        'VA' if Virginia, None otherwise
    """
    # Check birthPlace extension
    for ext in patient.get('extension', []):
        if ext.get('url') == 'http://hl7.org/fhir/StructureDefinition/patient-birthPlace':
            birth_state = ext.get('valueAddress', {}).get('state')
            if birth_state == 'Virginia':
                return 'VA'
    
    # Check address
    addresses = patient.get('address', [])
    if addresses:
        addr_state = addresses[0].get('state')
        if addr_state == 'Virginia' or addr_state == 'VA':
            return 'VA'
    
    return None


def aggregate_to_va_month(parsed_bundles: List[Dict]) -> pd.DataFrame:
    """
    Aggregate parsed FHIR bundles to VA×month grain.
    
    Args:
        parsed_bundles: List of dictionaries from parse_fhir_bundle()
        
    Returns:
        DataFrame with columns:
        - state_abbr: Always 'VA'
        - period_id: YYYYMM
        - synthea_encounters: COUNT(DISTINCT encounter_id)
        - synthea_dx_rate: (COUNT(DISTINCT condition_id) / COUNT(DISTINCT encounter_id)) × 1000
        - synthea_lab_oob_rate: Fraction of observations out of bounds [0-1]
        - low_precision_time: Always False (FHIR has precise timestamps)
        - ambiguous_geo: Always False (filtered to VA birthPlace/address)
    """
    # Flatten to encounter-level records
    rows = []
    for bundle in parsed_bundles:
        if bundle['state'] != 'VA':
            continue  # Filter to Virginia only
        
        customer_id = hash_customer_id(bundle['patient_id'])
        
        # Build encounter → period_id mapping
        encounter_periods = {enc['id']: enc['period_id'] for enc in bundle['encounters']}
        
        # Encounters
        for enc in bundle['encounters']:
            rows.append({
                'period_id': enc['period_id'],
                'encounter_id': enc['id'],
                'customer_id': customer_id
            })
        
        # Conditions (link to encounter period_id)
        for cond in bundle['conditions']:
            period_id = encounter_periods.get(cond['encounter_id'])
            if period_id:
                rows.append({
                    'period_id': period_id,
                    'condition_id': cond['id'],
                    'encounter_id': cond['encounter_id']
                })
        
        # Observations (link to encounter period_id)
        for obs in bundle['observations']:
            period_id = encounter_periods.get(obs['encounter_id'])
            if period_id:
                rows.append({
                    'period_id': period_id,
                    'observation_id': obs['id'],
                    'encounter_id': obs['encounter_id'],
                    'out_of_bounds': obs['out_of_bounds']
                })
    
    df = pd.DataFrame(rows)
    
    if df.empty:
        # Return empty DataFrame with correct schema
        return pd.DataFrame(columns=[
            'state_abbr', 'period_id', 'synthea_encounters', 
            'synthea_dx_rate', 'synthea_lab_oob_rate', 
            'low_precision_time', 'ambiguous_geo'
        ])
    
    # Aggregate by period_id
    agg_list = []
    for period_id in df['period_id'].unique():
        period_df = df[df['period_id'] == period_id]
        
        # Encounters: COUNT(DISTINCT encounter_id)
        encounters = period_df['encounter_id'].nunique()
        
        # Conditions: COUNT(DISTINCT condition_id)
        conditions = period_df['condition_id'].nunique() if 'condition_id' in period_df.columns else 0
        
        # Dx Rate: (conditions / encounters) × 1000
        dx_rate = (conditions / encounters * 1000) if encounters > 0 else None
        
        # Lab OOB Rate: fraction out of bounds
        obs_df = period_df.dropna(subset=['observation_id'])
        if not obs_df.empty:
            lab_oob_rate = obs_df['out_of_bounds'].mean()  # fraction True
        else:
            lab_oob_rate = None
        
        agg_list.append({
            'state_abbr': 'VA',
            'period_id': period_id,
            'synthea_encounters': encounters,
            'synthea_dx_rate': dx_rate,
            'synthea_lab_oob_rate': lab_oob_rate,
            'low_precision_time': False,
            'ambiguous_geo': False
        })
    
    return pd.DataFrame(agg_list)


def process_synthea(fhir_dir: str = 'data/raw/synthea/fhir') -> pd.DataFrame:
    """
    Main entry point: Process all Synthea FHIR bundles to VA×month aggregates.
    
    Args:
        fhir_dir: Path to directory containing .json FHIR Bundle files
        
    Returns:
        DataFrame with VA×month aggregates (synthea metrics)
        
    Raises:
        FileNotFoundError: If fhir_dir doesn't exist
        EnvironmentError: If CAPSTONE_HMAC_SALT not set
    """
    fhir_path = Path(fhir_dir)
    if not fhir_path.exists():
        raise FileNotFoundError(f"FHIR directory not found: {fhir_dir}")
    
    # Verify HMAC salt is set
    if not os.environ.get('CAPSTONE_HMAC_SALT'):
        raise EnvironmentError(
            "CAPSTONE_HMAC_SALT environment variable not set. "
            "Required for customer_id hashing."
        )
    
    # Parse all JSON files
    json_files = list(fhir_path.glob('*.json'))
    print(f"Found {len(json_files)} FHIR bundle files")
    
    parsed_bundles = []
    errors = 0
    for i, json_file in enumerate(json_files):
        if (i + 1) % 500 == 0:
            print(f"Processed {i + 1}/{len(json_files)} bundles...")
        
        try:
            bundle = parse_fhir_bundle(json_file)
            if bundle:
                parsed_bundles.append(bundle)
        except Exception as e:
            errors += 1
            if errors <= 10:  # Log first 10 errors
                print(f"Error parsing {json_file.name}: {e}")
    
    print(f"Successfully parsed {len(parsed_bundles)} bundles ({errors} errors)")
    
    # Aggregate to VA×month
    df = aggregate_to_va_month(parsed_bundles)
    
    print(f"Aggregated to {len(df)} VA×month records")
    print(f"Date range: {df['period_id'].min()} to {df['period_id'].max()}")
    
    return df


if __name__ == '__main__':
    # Demo execution
    import sys
    
    if 'CAPSTONE_HMAC_SALT' not in os.environ:
        print("ERROR: CAPSTONE_HMAC_SALT environment variable not set", file=sys.stderr)
        print("Set it before running: $env:CAPSTONE_HMAC_SALT='your-secret-salt'", file=sys.stderr)
        sys.exit(1)
    
    # Process Synthea FHIR bundles
    print("Processing Synthea FHIR bundles...")
    df = process_synthea()
    
    print("\nSummary:")
    print(f"Total VA×month records: {len(df)}")
    print(f"Period range: {df['period_id'].min()} - {df['period_id'].max()}")
    print(f"\nSample records:")
    print(df.head(10).to_string(index=False))
    
    # Save to interim
    output_path = 'data/interim/synthea_va_month.parquet'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"\nSaved to {output_path}")
