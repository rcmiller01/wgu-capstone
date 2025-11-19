# How to Reuse This Project

**Quick Start for Rural Health Networks**  
**Version**: 1.0  
**Last Updated**: November 11, 2025

---

## Overview

This project provides a **production-ready serverless FHIR data pipeline** with validation framework, processing scripts, and operational metrics. All components are designed for reusability and can be deployed to other rural health networks with minimal customization.

---

## 🎯 What You Get (Artifacts)

### 1. Validation Rule Packs (50+ Rules)

**Location**: `resources/rules/*.json`

**What**: Machine-readable validation rules organized by data source

**Reusability**: Adapt rules to your data sources by editing JSON files. No code changes needed.

**Example Rule** (from `core.json`):
```json
{
  "rule_id": "CORE_001",
  "field": "patient_id",
  "validation": "NOT NULL",
  "error_message": "Patient ID is required",
  "severity": "error"
}
```

**Customization Steps**:
1. Copy relevant rule pack (e.g., `synthea.json` for FHIR, `nhanes.json` for CDC data)
2. Edit `field` names to match your schema
3. Adjust `validation` logic for your business rules
4. Set `severity` (error, warning, info) based on your quality standards

### 2. Join Specification Template

**Location**: `resources/join_spec.json`

**What**: Defines join keys, synthetic flags, and aggregation logic

**Reusability**: Configure your join keys and quality flags without touching Python code

**Customization Steps**:
1. Update `join_keys` section with your data model (e.g., facility_id, encounter_date)
2. Define `synthetic_keys_and_flags` for your quality constraints (e.g., missing_demographics, incomplete_vitals)
3. Specify `aggregation_logic` for your reporting grain (facility, month, provider)

### 3. Processing Pipeline (FHIR/XPT/CSV)

**Location**: `src/pipeline/`

**What**: Extensible data processors for common health data formats

**Reusability**: Processors work out-of-the-box for FHIR R4, SAS XPT, and CSV. Extend for HL7v2, X12, or other formats.

**Key Files**:
- `process_raw_data.py`: Main orchestration
- `data_cleaning.py`: Cleaning functions (sentinels, nullable dtypes)
- `generate_cohort_summary.py`: Aggregation to cohort fact table

**Extension Example** (add HL7v2 processor):
```python
# Add to src/pipeline/process_hl7.py
def process_hl7(file_path):
    import hl7
    with open(file_path) as f:
        msg = hl7.parse(f.read())
    # Extract fields using hl7apy library
    return extracted_dataframe
```

### 4. Analysis Scripts (Bootstrap CIs, Sensitivity)

**Location**: `src/analysis/`

**What**: Statistical analysis with bootstrap confidence intervals and sensitivity testing

**Reusability**: Scripts are parameterized - change input file paths and run

**Key Scripts**:
- `generate_phase7_outputs.py`: Tables 1-2, Figures 1-3 with bootstrap 95% CI
- `sensitivity_analysis.py`: Robustness testing across exclusion scenarios

**Usage**:
```powershell
# Generate your tables and figures
python src/analysis/generate_phase7_outputs.py

# Run sensitivity analysis
python src/analysis/sensitivity_analysis.py
```

### 5. CI/CD Pipelines (GitHub Actions)

**Location**: `.github/workflows/`

**What**: Automated testing and linting on every commit

**Reusability**: Copy workflows to your repo, adjust Python versions if needed

**Pipelines**:
- `tests.yml`: pytest with coverage across Python 3.11/3.12
- `lint.yml`: black, ruff, mypy, pre-commit hooks

---

## 🚀 Deployment Guide (3 Paths)

### Path 1: Local Development (Quick Start)

**Use Case**: Testing on sample data before cloud deployment

**Steps**:
```powershell
# 1. Clone and setup
git clone https://github.com/rcmiller01/wgu-capstone.git
cd wgu-capstone
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Place your data in data/raw/
#    - FHIR JSON → data/raw/synthea/fhir/
#    - XPT files → data/raw/nhanes/
#    - CSV files → data/raw/vdh/

# 3. Edit resources/rules/*.json to match your data schema

# 4. Run pipeline
python -m src.pipeline

# 5. View results
# data/processed/cohort_fact_va.csv (aggregated metrics)
# data/processed/processed_data.parquet (row-level data)
```

**Time to First Results**: 30-60 minutes

### Path 2: AWS Lambda Deployment (Serverless)

**Use Case**: Production deployment with auto-scaling and pay-per-use pricing

**Prerequisites**:
- AWS account with Lambda, S3, CloudWatch permissions
- AWS CLI configured (`aws configure`)
- Terraform or SAM CLI for infrastructure-as-code

**Architecture**:
```
S3 Upload (Trigger) → Lambda Function → Validation → S3 Output
                           ↓
                    CloudWatch Logs (latency, pass/fail)
```

**Steps**:
1. **Package Lambda Function**:
   ```powershell
   # Create deployment package
   pip install -r requirements.txt -t package/
   cp -r src package/
   cp -r resources package/
   cd package && zip -r ../lambda_function.zip . && cd ..
   ```

2. **Create Lambda Function**:
   ```powershell
   aws lambda create-function \
     --function-name fhir-data-pipeline \
     --runtime python3.11 \
     --handler src.pipeline.process_raw_data.lambda_handler \
     --zip-file fileb://lambda_function.zip \
     --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
     --timeout 300 \
     --memory-size 1024
   ```

3. **Configure S3 Trigger**:
   ```powershell
   aws s3api put-bucket-notification-configuration \
     --bucket your-fhir-bucket \
     --notification-configuration file://s3-trigger.json
   ```

4. **Monitor**:
   ```powershell
   aws logs tail /aws/lambda/fhir-data-pipeline --follow
   ```

**Cost Estimate**: $0.20 per 1,000 files (assuming 1-second average execution)

### Path 3: Azure Functions Deployment (Alternative Serverless)

**Use Case**: Organizations with Azure infrastructure

**Prerequisites**:
- Azure account with Functions, Blob Storage permissions
- Azure CLI configured (`az login`)

**Steps**:
1. **Create Function App**:
   ```powershell
   az functionapp create \
     --resource-group your-rg \
     --name fhir-pipeline-func \
     --storage-account yourstorage \
     --runtime python \
     --runtime-version 3.11 \
     --functions-version 4 \
     --os-type Linux
   ```

2. **Deploy Code**:
   ```powershell
   func azure functionapp publish fhir-pipeline-func
   ```

3. **Configure Blob Trigger** (in `function.json`):
   ```json
   {
     "bindings": [
       {
         "type": "blobTrigger",
         "direction": "in",
         "name": "inputBlob",
         "path": "fhir-input/{name}",
         "connection": "AzureWebJobsStorage"
       }
     ]
   }
   ```

**Cost Estimate**: Similar to AWS (~$0.20 per 1,000 files)

---

## 🔧 Configuration for Your Use Case

### Scenario 1: Different FHIR Resources

**Problem**: You have Immunization, AllergyIntolerance instead of Encounter, Observation

**Solution**: Edit `resources/rules/synthea.json`

```json
{
  "rule_pack_name": "immunization_rules",
  "rules": [
    {
      "rule_id": "IMM_001",
      "field": "vaccineCode.coding[0].code",
      "validation": "NOT NULL",
      "error_message": "Vaccine code is required"
    }
  ]
}
```

### Scenario 2: Multi-Facility Network

**Problem**: Need to track metrics per facility, not just data source

**Solution**: Edit `resources/join_spec.json`

```json
{
  "join_keys": {
    "facility_id": {
      "description": "Unique facility identifier",
      "type": "string",
      "valid_values": ["FAC001", "FAC002", "FAC003"]
    }
  },
  "aggregation_logic": {
    "group_by": ["facility_id", "data_source"],
    "aggregates": {
      "n_records": "COUNT(*)",
      "validation_pass_rate": "SUM(validation_passed) / COUNT(*)"
    }
  }
}
```

### Scenario 3: Custom Quality Flags

**Problem**: Need to flag incomplete lab results, not just temporal/geographic issues

**Solution**: Add to `resources/join_spec.json` → `synthetic_keys_and_flags`

```json
{
  "incomplete_lab": {
    "description": "Lab observation missing result value",
    "type": "boolean",
    "values": {
      "0": "valueQuantity.value present",
      "1": "valueQuantity.value missing or null"
    },
    "impact": "Excluded from lab completeness rate calculations"
  }
}
```

---

## 📊 Performance Expectations

### Latency Benchmarks (From This Study)

| File Format | Avg Size | P50 Latency | P95 Latency | Throughput |
|:------------|:--------:|:-----------:|:-----------:|:----------:|
| FHIR JSON   | 2.4 MB   | 16.16s      | 42.06s      | ~60/hour   |
| XPT Binary  | 500 KB   | 5.94s       | 6.59s       | ~600/hour  |
| CSV Text    | 100 KB   | 3.45s       | 4.09s       | ~1,000/hour |

**Scaling**: Lambda/Functions auto-scale horizontally. 1,000 concurrent files = 1,000 concurrent function instances.

### Cost Projections

**AWS Lambda** (based on 1,000 files/day, 20s average execution):
- Compute: 1,000 × 20s × $0.0000166667/GB-sec × 1GB = **$0.33/day** = **$10/month**
- S3 Storage: 10GB × $0.023/GB = **$0.23/month**
- **Total**: ~$10-15/month

**Azure Functions** (Consumption Plan):
- Similar pricing: **$10-20/month** for 1,000 files/day

**Comparison to Manual**: 1,000 files × 20 min/file = 333 hours/month = **$6,660/month** (at $20/hour)

**ROI**: Automated pipeline saves **99.8%** of labor costs

---

## 🧪 Testing Your Deployment

### Step 1: Unit Tests (Before Deployment)

```powershell
# Run all tests
pytest tests/ -v --cov=src

# Should see:
# tests/test_schema.py::test_project_layout PASSED
# tests/test_schema.py::test_join_spec_structure PASSED
# ... (9 tests total)
# ======================== 9 passed in 2.34s ========================
```

### Step 2: Integration Test (After Deployment)

```powershell
# Upload test file to S3/Blob
aws s3 cp test_data/sample_fhir.json s3://your-bucket/input/

# Check CloudWatch logs for processing
aws logs tail /aws/lambda/fhir-data-pipeline --since 1m

# Verify output file created
aws s3 ls s3://your-bucket/output/
# Should see: processed_sample_fhir.parquet
```

### Step 3: Load Test (Performance Validation)

```powershell
# Upload 100 files simultaneously
for i in {1..100}; do
  aws s3 cp test_data/sample_$i.json s3://your-bucket/input/ &
done

# Monitor Lambda concurrent executions
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name ConcurrentExecutions \
  --dimensions Name=FunctionName,Value=fhir-data-pipeline \
  --start-time 2025-11-11T00:00:00Z \
  --end-time 2025-11-11T23:59:59Z \
  --period 300 \
  --statistics Maximum
```

---

## 📞 Support Resources

### Documentation

- **Full README**: [README.md](README.md)
- **Metrics Specification**: [docs/metrics_spec.md](docs/metrics_spec.md)
- **Validation Policy**: [docs/methods_validation_policy.md](docs/methods_validation_policy.md)
- **Cleaning Plan**: [docs/cleaning_plan.md](docs/cleaning_plan.md)

### Code Examples

- **FHIR Processing**: `src/pipeline/process_raw_data.py` lines 45-120
- **Validation Execution**: `src/pipeline/data_cleaning.py` lines 80-150
- **Bootstrap CIs**: `src/analysis/generate_phase7_outputs.py` lines 30-60

### Community

- **GitHub Issues**: https://github.com/rcmiller01/wgu-capstone/issues
- **Repository**: https://github.com/rcmiller01/wgu-capstone

---

## 🎓 Training Materials

### 5-Minute Quick Start Video (Conceptual Outline)

1. **Intro (0:00-0:30)**: Problem - rural health data is fragmented, manual entry is slow
2. **Architecture (0:30-1:30)**: S3 trigger → Lambda → Validation → Output
3. **Demo (1:30-3:00)**: Upload FHIR file, show CloudWatch logs, download processed data
4. **Customization (3:00-4:30)**: Edit rules/*.json, adjust join_spec.json, redeploy
5. **Wrap-up (4:30-5:00)**: Cost savings, next steps, support resources

### Runbook Template

**Daily Operations**:
- Monitor: CloudWatch dashboard for latency, pass rate, error count
- Alert: If pass rate drops below 90%, investigate validation failures
- Backup: S3 versioning enabled (automatic)

**Weekly Maintenance**:
- Review: Failed validations in `data/failed/` folder
- Update: Validation rules if new FHIR profiles introduced
- Test: Run `pytest tests/` to ensure no regressions

**Monthly Review**:
- Analyze: Latency trends (P50, P95) over time
- Optimize: If P95 > 60s, consider increasing Lambda memory
- Report: Generate monthly metrics with `src/analysis/generate_phase7_outputs.py`

---

## ✅ Checklist for Your Deployment

### Pre-Deployment

- [ ] Clone repository and install dependencies (`pip install -r requirements.txt`)
- [ ] Place sample data in `data/raw/` (10-20 files for testing)
- [ ] Edit `resources/rules/*.json` to match your data schema
- [ ] Edit `resources/join_spec.json` to define your join keys
- [ ] Run `pytest tests/` locally (all tests should pass)
- [ ] Run `python -m src.pipeline` locally (check `data/processed/` for outputs)

### Deployment (AWS Lambda)

- [ ] Create IAM role with S3, CloudWatch, Lambda permissions
- [ ] Package code into `lambda_function.zip`
- [ ] Create Lambda function with 1GB memory, 300s timeout
- [ ] Configure S3 bucket trigger on `s3://your-bucket/input/`
- [ ] Test with single file upload
- [ ] Monitor CloudWatch logs for errors
- [ ] Verify output in `s3://your-bucket/output/`

### Post-Deployment

- [ ] Set up CloudWatch dashboard (latency, pass rate, error count)
- [ ] Configure SNS alerts for error rate > 5%
- [ ] Document your customizations in `docs/deployment_notes.md`
- [ ] Schedule weekly review of failed validations
- [ ] Run monthly metrics report for stakeholders

---

## 🎯 Success Criteria (Adapted from This Study)

Your deployment is successful when:

1. **Validation Pass Rate** ≥ 95% (adjust target based on your data quality baseline)
2. **Median Latency (P50)** ≤ 30s per file (or your SLA requirement)
3. **Tail Latency (P95)** ≤ 120s per file (ensures consistent user experience)
4. **Cost** ≤ $0.20 per 1,000 files (or < 1% of manual entry cost)
5. **Uptime** ≥ 99.5% (serverless inherently high-availability)

---

**Version**: 1.0  
**License**: MIT (see LICENSE file)  
**Repository**: https://github.com/rcmiller01/health-data-lake
**Last Updated**: November 11, 2025

---

**Ready to Deploy?** Start with **Path 1 (Local Development)** to validate on your data, then move to **Path 2 or 3 (Serverless)** for production scale.
