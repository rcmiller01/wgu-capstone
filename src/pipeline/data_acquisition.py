"""
Data acquisition module for WGU D610 Capstone.

Downloads/generates all four data sources:
1. Synthea - synthetic patient records (FHIR JSON)
2. NHANES - CDC survey data (XPT → CSV)
3. Virginia DoH - state health data (CSV)
4. NIH Chest X-Ray - medical imaging (PNG + metadata)

Usage:
    python -m src.pipeline.data_acquisition --all
    python -m src.pipeline.data_acquisition --synthea --n-patients 5000
    python -m src.pipeline.data_acquisition --nhanes --cycles 2017-2018,2019-2020
    python -m src.pipeline.data_acquisition --vdh
    python -m src.pipeline.data_acquisition --nih --n-images 2000
"""
from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import urllib.request
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
SYNTHEA_DIR = RAW_DIR / "synthea"
NHANES_DIR = RAW_DIR / "nhanes"
VDH_DIR = RAW_DIR / "vdh"
NIH_DIR = RAW_DIR / "nih_xray"

# Ensure directories exist
for directory in [RAW_DIR, SYNTHEA_DIR, NHANES_DIR, VDH_DIR, NIH_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class AcquisitionLogger:
    """Track data acquisition operations."""
    
    def __init__(self, log_path: Path = DATA_DIR / "acquisition_log.txt"):
        self.log_path = log_path
    
    def log(self, source: str, status: str, details: dict):
        """Append acquisition event to log."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "source": source,
            "status": status,
            "details": details
        }
        
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.info(f"{source}: {status} - {details}")


acq_logger = AcquisitionLogger()


def generate_synthea_data(
    n_patients: int = 5000,
    seed: int = 12345,
    state: str = "Virginia",
    output_dir: Path = SYNTHEA_DIR
) -> bool:
    """
    Generate synthetic patient records using Synthea.
    
    Args:
        n_patients: Number of patients to generate
        seed: Random seed for reproducibility
        state: US state for demographics (default: Virginia)
        output_dir: Output directory for FHIR JSON files
    
    Returns:
        True if successful, False otherwise
    
    Prerequisites:
        - Java 11+ installed
        - Synthea JAR downloaded to resources/synthea-with-dependencies.jar
        
    Download Synthea JAR:
        https://github.com/synthetichealth/synthea/releases/latest/download/synthea-with-dependencies.jar
    """
    logger.info(f"Generating Synthea data: {n_patients} patients, seed={seed}, state={state}")
    
    # Check for Synthea JAR
    synthea_jar = PROJECT_ROOT / "resources" / "synthea-with-dependencies.jar"
    
    if not synthea_jar.exists():
        logger.error(f"Synthea JAR not found at {synthea_jar}")
        logger.error("Download from: https://github.com/synthetichealth/synthea/releases/latest")
        acq_logger.log("synthea", "FAILED", {"reason": "JAR not found", "expected_path": str(synthea_jar)})
        return False
    
    # Check for Java
    try:
        java_version = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Java found: {java_version.stderr.split()[2]}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Java not found. Install Java 11+ from https://adoptium.net/")
        acq_logger.log("synthea", "FAILED", {"reason": "Java not installed"})
        return False
    
    # Prepare output directory
    fhir_output = output_dir / "fhir"
    fhir_output.mkdir(parents=True, exist_ok=True)
    
    # Build command
    cmd = [
        "java",
        "-jar", str(synthea_jar),
        "-p", str(n_patients),
        "-s", str(seed),
        "--exporter.fhir.export=true",
        f"--exporter.baseDirectory={output_dir}",
        state
    ]
    
    try:
        logger.info(f"Running Synthea (this may take 10-30 minutes for {n_patients} patients)...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=PROJECT_ROOT)
        
        # Count generated files
        fhir_files = list(fhir_output.glob("*.json"))
        file_count = len(fhir_files)
        
        # Calculate total size
        total_size_mb = sum(f.stat().st_size for f in fhir_files) / (1024 * 1024)
        
        # Save metadata
        metadata = {
            "n_patients": n_patients,
            "seed": seed,
            "state": state,
            "generated_files": file_count,
            "total_size_mb": round(total_size_mb, 2),
            "generation_date": datetime.now().isoformat()
        }
        
        with open(output_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        acq_logger.log("synthea", "SUCCESS", metadata)
        logger.info(f"Synthea generation complete: {file_count} files, {total_size_mb:.2f} MB")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Synthea generation failed: {e.stderr}")
        acq_logger.log("synthea", "FAILED", {"error": str(e)})
        return False


def download_file(url: str, dest_path: Path) -> bool:
    """Download a file with progress indication."""
    try:
        logger.info(f"Downloading {url} -> {dest_path.name}")
        
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            
            with open(dest_path, 'wb') as f:
                downloaded = 0
                chunk_size = 8192
                
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
        
        print()  # New line after progress
        logger.info(f"Downloaded {dest_path.name} ({dest_path.stat().st_size / 1024:.1f} KB)")
        return True
        
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False


def download_nhanes_data(
    cycles: List[str] = None,
    components: List[str] = None,
    output_dir: Path = NHANES_DIR
) -> bool:
    """
    Download NHANES survey data from CDC.
    
    Args:
        cycles: Survey cycles to download (e.g., ["2017-2018", "2019-2020"])
        components: Data components (e.g., ["DEMO", "BMX", "TCHOL"])
        output_dir: Output directory
    
    Returns:
        True if all downloads successful
    
    NHANES URLs:
        https://wwwn.cdc.gov/Nchs/Nhanes/[CYCLE]/[COMPONENT]_[LETTER].XPT
        
    Examples:
        2017-2018 Demographics: DEMO_J.XPT (J = 2017-2018)
        2019-2020 Demographics: DEMO_K.XPT (K = 2019-2020)
    """
    if cycles is None:
        cycles = ["2017-2018", "2019-2020"]
    
    if components is None:
        # Select key components for health data
        components = [
            "DEMO",   # Demographics
            "BMX",    # Body Measures (height, weight, BMI)
            "TCHOL",  # Total Cholesterol
            "BPQ"     # Blood Pressure Questionnaire
        ]
    
    # Cycle letter codes
    cycle_codes = {
        "2017-2018": "J",
        "2019-2020": "K"
    }
    
    base_url = "https://wwwn.cdc.gov/Nchs/Nhanes"
    downloaded_files = []
    failed_downloads = []
    
    for cycle in cycles:
        if cycle not in cycle_codes:
            logger.warning(f"Unknown cycle: {cycle}, skipping")
            continue
        
        cycle_letter = cycle_codes[cycle]
        cycle_dir = output_dir / cycle
        cycle_dir.mkdir(parents=True, exist_ok=True)
        
        for component in components:
            filename = f"{component}_{cycle_letter}.XPT"
            url = f"{base_url}/{cycle}/{filename}"
            dest = cycle_dir / filename
            
            if dest.exists():
                logger.info(f"File already exists: {filename}, skipping")
                downloaded_files.append(str(dest))
                continue
            
            if download_file(url, dest):
                downloaded_files.append(str(dest))
            else:
                failed_downloads.append(url)
    
    # Log results
    acq_logger.log("nhanes", "COMPLETE" if not failed_downloads else "PARTIAL", {
        "cycles": cycles,
        "components": components,
        "downloaded_files": len(downloaded_files),
        "failed_downloads": len(failed_downloads),
        "files": downloaded_files
    })
    
    if failed_downloads:
        logger.warning(f"Some downloads failed: {failed_downloads}")
        return False
    
    logger.info(f"NHANES download complete: {len(downloaded_files)} files")
    
    # Create README
    readme_content = f"""# NHANES Data

Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Cycles
{', '.join(cycles)}

## Components
- DEMO: Demographics (age, gender, race, income)
- BMX: Body Measures (height, weight, BMI, waist circumference)
- TCHOL: Total Cholesterol
- BPQ: Blood Pressure Questionnaire

## Files
{chr(10).join(f'- {Path(f).name}' for f in downloaded_files)}

## Usage
Convert XPT to CSV using Python:
```python
import pandas as pd
df = pd.read_sas('DEMO_J.XPT', format='xport')
df.to_csv('DEMO_J.csv', index=False)
```

## Documentation
- Codebooks: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx
- Survey Design: https://wwwn.cdc.gov/nchs/nhanes/analyticguidelines.aspx
"""
    
    with open(output_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    return True


def download_vdh_data(
    datasets: List[str] = None,
    output_dir: Path = VDH_DIR
) -> bool:
    """
    Download Virginia Department of Health data.
    
    Args:
        datasets: List of dataset IDs or URLs
        output_dir: Output directory
    
    Returns:
        True if successful
    
    Note:
        This is a placeholder. Actual implementation depends on VDH data portal structure.
        Users may need to manually download CSV files from:
        https://data.virginia.gov/browse?tags=health
    """
    logger.info("VDH data acquisition placeholder")
    logger.info("Manual download required from: https://data.virginia.gov/browse?tags=health")
    
    # Create placeholder README
    readme_content = """# Virginia Department of Health Data

## Manual Download Required

Visit: https://data.virginia.gov/browse?tags=health

### Recommended Datasets

1. **COVID-19 Cases by Health District**
   - County-level case counts and rates
   - Search: "COVID-19" + "County" or "Health District"

2. **Chronic Disease Indicators**
   - Diabetes, hypertension prevalence by district
   - Search: "Chronic Disease" or "BRFSS"

3. **Health Professional Shortage Areas (HPSA)**
   - Rural health access metrics
   - Search: "HPSA" or "Health Professional Shortage"

### Download Instructions

1. Go to https://data.virginia.gov/browse?tags=health
2. Filter by:
   - Tags: health
   - Date Range: 2015-present
   - Format: CSV
3. Download datasets to this directory (`data/raw/vdh/`)
4. Rename files descriptively (e.g., `covid_cases_by_district.csv`)

### API Access (Optional)

For automated downloads, register for free API token:
- https://dev.socrata.com/
- Use Socrata Open Data API (SODA)

Example:
```python
import requests
dataset_id = "abc-123"  # From dataset URL
url = f"https://data.virginia.gov/resource/{dataset_id}.json"
response = requests.get(url)
data = response.json()
```
"""
    
    with open(output_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    acq_logger.log("vdh", "MANUAL_REQUIRED", {
        "message": "User must manually download from data.virginia.gov",
        "url": "https://data.virginia.gov/browse?tags=health"
    })
    
    logger.info(f"Created README: {output_dir / 'README.md'}")
    logger.warning("VDH data requires manual download - see README for instructions")
    
    return True


def download_nih_xray_sample(
    n_images: int = 2000,
    output_dir: Path = NIH_DIR,
    stratify_by_label: bool = True
) -> bool:
    """
    Download NIH Chest X-Ray dataset sample.
    
    Args:
        n_images: Number of images to download (full dataset = 112,120)
        output_dir: Output directory
        stratify_by_label: If True, sample evenly across pathology labels
    
    Returns:
        True if successful
    
    Note:
        Full dataset is ~42 GB. This function provides instructions for:
        1. Kaggle CLI download (requires account + API key)
        2. NIH Box download (manual)
        3. Sampling strategy to reduce size
    """
    logger.info(f"NIH Chest X-Ray dataset - sampling {n_images} images")
    
    # Create placeholder README
    readme_content = f"""# NIH Chest X-Ray Dataset

## Dataset Information

- **Full Dataset**: 112,120 frontal-view X-ray images
- **Size**: ~42 GB (full), ~{(n_images/112120)*42:.1f} GB (sample of {n_images})
- **Labels**: 14 pathology classes (NLP-derived from radiology reports)
- **Source**: NIH Clinical Center

## Download Options

### Option 1: Kaggle CLI (Recommended)

1. Install Kaggle CLI:
   ```bash
   pip install kaggle
   ```

2. Get API credentials:
   - Go to https://www.kaggle.com/settings
   - Click "Create New API Token" (downloads `kaggle.json`)
   - Place in `~/.kaggle/kaggle.json` (Linux/Mac) or `%USERPROFILE%\\.kaggle\\kaggle.json` (Windows)

3. Download dataset:
   ```bash
   kaggle datasets download -d nih-chest-xrays/data -p data/raw/nih_xray/
   unzip data/raw/nih_xray/data.zip -d data/raw/nih_xray/
   ```

4. Sample images:
   ```python
   import pandas as pd
   import shutil
   from pathlib import Path
   
   # Load metadata
   meta = pd.read_csv('data/raw/nih_xray/Data_Entry_2017.csv')
   
   # Stratified sample ({n_images} images)
   sample = meta.groupby('Finding Labels', group_keys=False).apply(
       lambda x: x.sample(min(len(x), {n_images}//14))
   ).sample({n_images})
   
   # Copy sampled images
   sample_dir = Path('data/raw/nih_xray/sample')
   sample_dir.mkdir(exist_ok=True)
   
   for img_name in sample['Image Index']:
       src = Path('data/raw/nih_xray/images') / img_name
       if src.exists():
           shutil.copy(src, sample_dir / img_name)
   
   # Save sample metadata
   sample.to_csv('data/raw/nih_xray/sample_metadata.csv', index=False)
   ```

### Option 2: NIH Box (Manual Download)

1. Visit: https://nihcc.app.box.com/v/ChestXray-NIHCC
2. Download `images_001.tar.gz` through `images_012.tar.gz` (pick a subset for sample)
3. Extract to `data/raw/nih_xray/images/`
4. Download `Data_Entry_2017.csv` (metadata)

### Option 3: Pre-sampled Dataset (If Available)

Check if course provides a pre-sampled version for students.

## Sampling Strategy

For {n_images} images:
- **Stratified by label**: ~{n_images//14} images per pathology class
- **Ensures class balance**: Avoids "No Finding" majority class bias
- **Reduces storage**: From 42 GB to ~{(n_images/112120)*42:.1f} GB

## Dataset Structure

```
data/raw/nih_xray/
├── images/              # Full dataset (or sampled subset)
│   ├── 00000001_000.png
│   ├── 00000001_001.png
│   └── ...
├── sample/              # Stratified sample ({n_images} images)
│   └── [sampled images]
├── Data_Entry_2017.csv  # Full metadata
├── sample_metadata.csv  # Sample metadata
└── README.md            # This file
```

## Citation

Wang, X., Peng, Y., Lu, L., Lu, Z., Bagheri, M., & Summers, R. M. (2017). 
ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised 
Classification and Localization of Common Thorax Diseases. 
*IEEE CVPR*, 2017. https://doi.org/10.1109/CVPR.2017.369

## License

CC0 (Public Domain)
"""
    
    with open(output_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    acq_logger.log("nih_xray", "MANUAL_REQUIRED", {
        "message": "User must download via Kaggle or NIH Box - see README",
        "target_sample_size": n_images,
        "full_dataset_size_gb": 42,
        "estimated_sample_size_gb": round((n_images/112120)*42, 1)
    })
    
    logger.info(f"Created README: {output_dir / 'README.md'}")
    logger.warning("NIH X-Ray data requires manual download - see README for instructions")
    
    return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Acquire data sources for WGU D610 Capstone",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Source selection
    parser.add_argument('--all', action='store_true', help='Acquire all data sources')
    parser.add_argument('--synthea', action='store_true', help='Generate Synthea data')
    parser.add_argument('--nhanes', action='store_true', help='Download NHANES data')
    parser.add_argument('--vdh', action='store_true', help='Setup VDH download instructions')
    parser.add_argument('--nih', action='store_true', help='Setup NIH X-Ray download instructions')
    
    # Synthea options
    parser.add_argument('--n-patients', type=int, default=5000, help='Number of Synthea patients (default: 5000)')
    parser.add_argument('--seed', type=int, default=12345, help='Random seed (default: 12345)')
    parser.add_argument('--state', type=str, default='Virginia', help='State for demographics (default: Virginia)')
    
    # NHANES options
    parser.add_argument('--cycles', type=str, default='2017-2018,2019-2020', 
                       help='NHANES cycles (default: 2017-2018,2019-2020)')
    
    # NIH options
    parser.add_argument('--n-images', type=int, default=2000, help='Number of NIH images to sample (default: 2000)')
    
    args = parser.parse_args()
    
    # If no specific source selected and not --all, show help
    if not any([args.all, args.synthea, args.nhanes, args.vdh, args.nih]):
        parser.print_help()
        sys.exit(1)
    
    success = True
    
    # Run selected acquisitions
    if args.all or args.synthea:
        logger.info("=" * 60)
        logger.info("SYNTHEA DATA GENERATION")
        logger.info("=" * 60)
        success &= generate_synthea_data(
            n_patients=args.n_patients,
            seed=args.seed,
            state=args.state
        )
    
    if args.all or args.nhanes:
        logger.info("=" * 60)
        logger.info("NHANES DATA DOWNLOAD")
        logger.info("=" * 60)
        cycles = args.cycles.split(',')
        success &= download_nhanes_data(cycles=cycles)
    
    if args.all or args.vdh:
        logger.info("=" * 60)
        logger.info("VIRGINIA DOH DATA SETUP")
        logger.info("=" * 60)
        success &= download_vdh_data()
    
    if args.all or args.nih:
        logger.info("=" * 60)
        logger.info("NIH CHEST X-RAY SETUP")
        logger.info("=" * 60)
        success &= download_nih_xray_sample(n_images=args.n_images)
    
    # Summary
    logger.info("=" * 60)
    if success:
        logger.info("DATA ACQUISITION COMPLETE")
    else:
        logger.warning("DATA ACQUISITION COMPLETED WITH ERRORS")
    logger.info(f"Check acquisition log: {DATA_DIR / 'acquisition_log.txt'}")
    logger.info("=" * 60)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
