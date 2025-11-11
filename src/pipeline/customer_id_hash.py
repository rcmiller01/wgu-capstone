"""
customer_id_hash.py
-------------------
Generate deterministic, privacy-preserving customer identifiers using HMAC-SHA256.

Purpose:
- Hash patient IDs to customer_id using HMAC-SHA256 with env-based salt
- Ensure deterministic output (same input → same hash)
- Normalize inputs (trim whitespace, uppercase) before hashing

Environment Variables:
- CAPSTONE_HMAC_SALT: Secret salt for HMAC (required)

Usage:
    from src.pipeline.customer_id_hash import hash_customer_id
    
    customer_id = hash_customer_id("patient-123")
    # Returns: deterministic hex string (64 chars)
"""

import hashlib
import hmac
import os
from typing import Optional


def hash_customer_id(patient_id: str) -> str:
    """
    Generate deterministic customer_id from patient_id using HMAC-SHA256.
    
    Process:
    1. Normalize patient_id: strip whitespace, convert to uppercase
    2. Encode normalized value as UTF-8
    3. Hash with HMAC-SHA256 using CAPSTONE_HMAC_SALT
    4. Return hexdigest (64-character string)
    
    Args:
        patient_id: Raw patient identifier from source system
        
    Returns:
        64-character hexadecimal customer_id
        
    Raises:
        ValueError: If patient_id is empty after normalization
        EnvironmentError: If CAPSTONE_HMAC_SALT not set
        
    Examples:
        >>> os.environ['CAPSTONE_HMAC_SALT'] = 'test-salt-123'
        >>> hash_customer_id('patient-abc')
        'e8f3d1c2b4a5...'  # 64 chars
        >>> hash_customer_id('  PATIENT-ABC  ')
        'e8f3d1c2b4a5...'  # Same hash (normalized)
        >>> hash_customer_id('patient-abc') == hash_customer_id('patient-abc')
        True  # Deterministic
    """
    # Get salt from environment
    salt = os.environ.get('CAPSTONE_HMAC_SALT')
    if not salt:
        raise EnvironmentError(
            "CAPSTONE_HMAC_SALT environment variable not set. "
            "This is required for customer_id hashing."
        )
    
    # Normalize: trim whitespace, uppercase
    normalized = patient_id.strip().upper()
    if not normalized:
        raise ValueError(f"patient_id cannot be empty after normalization: '{patient_id}'")
    
    # Generate HMAC-SHA256 hash
    h = hmac.new(
        key=salt.encode('utf-8'),
        msg=normalized.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    
    return h.hexdigest()


def batch_hash_customer_ids(patient_ids: list[str]) -> dict[str, str]:
    """
    Hash multiple patient IDs to customer IDs in batch.
    
    Args:
        patient_ids: List of raw patient identifiers
        
    Returns:
        Dictionary mapping normalized patient_id → customer_id
        
    Examples:
        >>> batch_hash_customer_ids(['patient-1', 'patient-2'])
        {'PATIENT-1': 'abc123...', 'PATIENT-2': 'def456...'}
    """
    results = {}
    for pid in patient_ids:
        normalized = pid.strip().upper()
        results[normalized] = hash_customer_id(pid)
    return results


if __name__ == '__main__':
    # Quick demonstration
    import sys
    
    if 'CAPSTONE_HMAC_SALT' not in os.environ:
        print("ERROR: CAPSTONE_HMAC_SALT environment variable not set", file=sys.stderr)
        print("Set it before running: $env:CAPSTONE_HMAC_SALT='your-secret-salt'", file=sys.stderr)
        sys.exit(1)
    
    # Demo with sample IDs
    samples = ['patient-001', 'patient-002', '  patient-001  ', 'PATIENT-001']
    print("Customer ID Hashing Demo")
    print("=" * 80)
    for sample in samples:
        cid = hash_customer_id(sample)
        print(f"Input: '{sample}' → customer_id: {cid}")
    
    print("\nDeterminism Check:")
    print(f"hash('patient-001') == hash('  PATIENT-001  '): {hash_customer_id('patient-001') == hash_customer_id('  PATIENT-001  ')}")
