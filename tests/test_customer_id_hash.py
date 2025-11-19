"""
test_customer_id_hash.py
-------------------------
Unit tests for customer_id hashing utility.

Tests:
- Determinism: Same input produces same hash
- Normalization: Whitespace/case variants produce same hash
- Salt dependency: Different salts produce different hashes
- Error handling: Missing salt, empty input
- 10-row determinism check
"""

import os
import pytest
from src.pipeline.customer_id_hash import hash_customer_id, batch_hash_customer_ids


@pytest.fixture
def set_salt():
    """Set PIPELINE_HMAC_SALT for testing."""
    original = os.environ.get('PIPELINE_HMAC_SALT')
    os.environ['PIPELINE_HMAC_SALT'] = 'test-salt-for-unit-tests-only'
    yield
    # Restore original
    if original:
        os.environ['PIPELINE_HMAC_SALT'] = original
    else:
        del os.environ['PIPELINE_HMAC_SALT']


class TestCustomerIdHashing:
    """Test suite for customer_id hashing."""
    
    def test_determinism_single_call(self, set_salt):
        """Test: Same input produces same hash (determinism)."""
        patient_id = 'patient-12345'
        hash1 = hash_customer_id(patient_id)
        hash2 = hash_customer_id(patient_id)
        
        assert hash1 == hash2, "Hash must be deterministic for same input"
        assert len(hash1) == 64, "SHA256 hex digest should be 64 characters"
    
    def test_determinism_10_rows(self, set_salt):
        """Test: 10 patient IDs hash deterministically across multiple calls."""
        patient_ids = [
            'patient-001',
            'patient-002',
            'patient-003',
            'patient-004',
            'patient-005',
            'patient-006',
            'patient-007',
            'patient-008',
            'patient-009',
            'patient-010'
        ]
        
        # Hash all IDs (first pass)
        first_pass = {pid: hash_customer_id(pid) for pid in patient_ids}
        
        # Hash all IDs again (second pass)
        second_pass = {pid: hash_customer_id(pid) for pid in patient_ids}
        
        # Assert determinism for each ID
        for pid in patient_ids:
            assert first_pass[pid] == second_pass[pid], \
                f"Hash for {pid} must be deterministic across calls"
        
        # Assert all hashes are 64 characters
        for pid, cid in first_pass.items():
            assert len(cid) == 64, f"Hash for {pid} should be 64 chars, got {len(cid)}"
        
        # Assert all hashes are unique
        hash_values = list(first_pass.values())
        assert len(hash_values) == len(set(hash_values)), \
            "All 10 patient IDs should produce unique hashes"
    
    def test_normalization_whitespace(self, set_salt):
        """Test: Whitespace is trimmed before hashing."""
        variants = [
            'patient-abc',
            '  patient-abc',
            'patient-abc  ',
            '  patient-abc  ',
            '\tpatient-abc\n'
        ]
        
        hashes = [hash_customer_id(v) for v in variants]
        assert len(set(hashes)) == 1, \
            "All whitespace variants should produce same hash"
    
    def test_normalization_case(self, set_salt):
        """Test: Case is normalized to uppercase before hashing."""
        variants = [
            'patient-abc',
            'PATIENT-ABC',
            'Patient-Abc',
            'PaTiEnT-aBc'
        ]
        
        hashes = [hash_customer_id(v) for v in variants]
        assert len(set(hashes)) == 1, \
            "All case variants should produce same hash"
    
    def test_normalization_combined(self, set_salt):
        """Test: Combined whitespace + case normalization."""
        canonical = hash_customer_id('patient-xyz')
        
        variants = [
            '  PATIENT-XYZ  ',
            '\tPatient-Xyz\n',
            'patient-xyz   ',
            '   PATIENT-xyz'
        ]
        
        for variant in variants:
            assert hash_customer_id(variant) == canonical, \
                f"Variant '{variant}' should match canonical"
    
    def test_salt_dependency(self):
        """Test: Different salts produce different hashes."""
        patient_id = 'patient-test'
        
        # Hash with first salt
        os.environ['PIPELINE_HMAC_SALT'] = 'salt-one'
        hash1 = hash_customer_id(patient_id)
        
        # Hash with second salt
        os.environ['PIPELINE_HMAC_SALT'] = 'salt-two'
        hash2 = hash_customer_id(patient_id)
        
        assert hash1 != hash2, \
            "Different salts should produce different hashes"
        
        # Cleanup
        del os.environ['PIPELINE_HMAC_SALT']
    
    def test_error_missing_salt(self):
        """Test: Raises error if PIPELINE_HMAC_SALT not set."""
        # Ensure salt is not set
        if 'PIPELINE_HMAC_SALT' in os.environ:
            del os.environ['PIPELINE_HMAC_SALT']
        
        with pytest.raises(EnvironmentError, match="PIPELINE_HMAC_SALT"):
            hash_customer_id('patient-001')
    
    def test_error_empty_input(self, set_salt):
        """Test: Raises error for empty patient_id after normalization."""
        with pytest.raises(ValueError, match="cannot be empty"):
            hash_customer_id('')
        
        with pytest.raises(ValueError, match="cannot be empty"):
            hash_customer_id('   ')
        
        with pytest.raises(ValueError, match="cannot be empty"):
            hash_customer_id('\t\n')
    
    def test_batch_hashing(self, set_salt):
        """Test: batch_hash_customer_ids processes multiple IDs correctly."""
        patient_ids = ['patient-a', 'patient-b', 'patient-c']
        
        result = batch_hash_customer_ids(patient_ids)
        
        # Check keys are normalized
        assert set(result.keys()) == {'PATIENT-A', 'PATIENT-B', 'PATIENT-C'}
        
        # Check values match individual hashing
        for pid in patient_ids:
            normalized = pid.upper()
            assert result[normalized] == hash_customer_id(pid)
    
    def test_hash_uniqueness(self, set_salt):
        """Test: Different inputs produce different hashes."""
        ids = [f'patient-{i:04d}' for i in range(100)]
        hashes = [hash_customer_id(pid) for pid in ids]
        
        assert len(hashes) == len(set(hashes)), \
            "All 100 different patient IDs should produce unique hashes"


if __name__ == '__main__':
    # Run determinism check standalone
    os.environ['PIPELINE_HMAC_SALT'] = 'test-salt-standalone'
    
    print("10-Row Determinism Check")
    print("=" * 80)
    
    test_ids = [f'patient-{i:03d}' for i in range(1, 11)]
    
    # First pass
    print("\nFirst pass:")
    first = {}
    for tid in test_ids:
        cid = hash_customer_id(tid)
        first[tid] = cid
        print(f"{tid} → {cid}")
    
    # Second pass
    print("\nSecond pass:")
    second = {}
    for tid in test_ids:
        cid = hash_customer_id(tid)
        second[tid] = cid
        print(f"{tid} → {cid}")
    
    # Verify
    print("\nVerification:")
    all_match = all(first[tid] == second[tid] for tid in test_ids)
    print(f"All hashes match: {all_match}")
    
    if all_match:
        print("✅ PASS: Determinism verified for 10 rows")
    else:
        print("❌ FAIL: Hashes do not match across passes")
        for tid in test_ids:
            if first[tid] != second[tid]:
                print(f"  Mismatch: {tid}")

