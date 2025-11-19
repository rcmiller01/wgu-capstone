"""
run_pipeline.py
---------------
Master pipeline runner to execute full data processing workflow.

Purpose:
- Execute all processors in sequence
- Build CohortFact_VA table
- Generate summary report
- Run validation tests

Steps:
1. Process Synthea FHIR bundles → data/interim/synthea_va_month.parquet
2. Process NHANES surveys → data/interim/nhanes_va_month.parquet
3. Process VDH CSVs → data/interim/vdh_va_month.parquet
4. Process NIH metadata → data/interim/nih_va_month.parquet
5. Build CohortFact_VA → data/processed/cohort_fact_va.parquet
6. Generate summary report → reports/cohort_fact_summary.md
7. Run validation tests → pytest output

Usage:
    python src/pipeline/run_pipeline.py
    
Environment Variables:
    PIPELINE_HMAC_SALT: Required for customer_id hashing
"""

import os
import sys
from datetime import datetime


def check_environment():
    """Verify required environment variables are set."""
    if not os.environ.get('PIPELINE_HMAC_SALT'):
        print("ERROR: PIPELINE_HMAC_SALT environment variable not set")
        print("Set it before running: $env:PIPELINE_HMAC_SALT='your-secret-salt'")
        sys.exit(1)
    
    print("✓ Environment check passed")


def run_step(step_num: int, step_name: str, func, *args, **kwargs):
    """Execute a pipeline step with error handling."""
    print(f"\n{'=' * 80}")
    print(f"STEP {step_num}: {step_name}")
    print(f"{'=' * 80}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        result = func(*args, **kwargs)
        print(f"\n✓ Step {step_num} completed successfully")
        return result
    except Exception as e:
        print(f"\n✗ Step {step_num} failed: {e}")
        raise


def main():
    """Execute full pipeline."""
    print("Health Data Lake - Data Pipeline Execution")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    check_environment()
    
    # Step 1: Process Synthea
    from src.pipeline.synthea_processor import process_synthea
    synthea_df = run_step(1, "Process Synthea FHIR Bundles", process_synthea)
    
    # Step 2: Process NHANES
    from src.pipeline.nhanes_processor import process_nhanes
    nhanes_df = run_step(2, "Process NHANES Surveys", process_nhanes)
    
    # Step 3: Process VDH
    from src.pipeline.vdh_processor import process_vdh
    vdh_df = run_step(3, "Process VDH Data", process_vdh)
    
    # Step 4: Process NIH
    from src.pipeline.nih_processor import process_nih
    nih_df = run_step(4, "Process NIH Metadata", process_nih)
    
    # Step 5: Build CohortFact_VA
    from src.pipeline.build_cohort_fact import build_cohort_fact
    cohort_fact_df = run_step(5, "Build CohortFact_VA Table", build_cohort_fact)
    
    # Step 6: Generate Summary Report
    from src.analysis.generate_summary import generate_summary
    summary_report = run_step(
        6, 
        "Generate Summary Report", 
        generate_summary,
        'data/processed/cohort_fact_va.parquet'
    )
    
    # Save summary
    os.makedirs('reports', exist_ok=True)
    with open('reports/cohort_fact_summary.md', 'w') as f:
        f.write(summary_report)
    print("\nSummary report saved to: reports/cohort_fact_summary.md")
    
    # Step 7: Run Validation Tests
    print(f"\n{'=' * 80}")
    print(f"STEP 7: Run Validation Tests")
    print(f"{'=' * 80}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    import pytest
    exit_code = pytest.main([
        'tests/test_cohort_fact_validation.py',
        '-v',
        '--tb=short'
    ])
    
    if exit_code == 0:
        print("\n✓ All validation tests passed")
    else:
        print(f"\n✗ Some validation tests failed (exit code: {exit_code})")
    
    # Final summary
    print(f"\n{'=' * 80}")
    print("PIPELINE EXECUTION COMPLETE")
    print(f"{'=' * 80}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nOutputs:")
    print(f"  - data/interim/synthea_va_month.parquet")
    print(f"  - data/interim/nhanes_va_month.parquet")
    print(f"  - data/interim/vdh_va_month.parquet")
    print(f"  - data/interim/nih_va_month.parquet")
    print(f"  - data/processed/cohort_fact_va.parquet")
    print(f"  - reports/cohort_fact_summary.md")
    print(f"\nNext Steps:")
    print(f"  1. Review summary report: reports/cohort_fact_summary.md")
    print(f"  2. Check validation test results above")
    print(f"  3. If satisfied, proceed to statistical tests (Step 4)")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nPIPELINE FAILED: {e}")
        sys.exit(1)
