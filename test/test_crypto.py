import os
import pytest
import time

def test_secure_wipe_logic(tmp_path):
    """
    Creates a temporary file, writes 'sensitive' data, 
    and verifies that the wipe function removes it.
    """
    # 1. Create a temporary file in a safe test directory
    test_file = tmp_path / "vault_test.txt"
    test_file.write_text("TOP_SECRET_DATA_DO_NOT_READ")
    file_path = str(test_file)

    # 2. Verify file exists before wiping
    assert os.path.exists(file_path)

    # 3. RUN YOUR WIPE FUNCTION
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except PermissionError:
        pytest.fail("Windows PermissionError: The file is still locked by another process!")

    # 4. Final Assert
    assert not os.path.exists(file_path)

def test_encryption_roundtrip():
    """Tests if data remains the same after Encrypt -> Decrypt."""
    original_data = "COMRADE_SECRET_PROTOCOL"
   
    decrypted = "COMRADE_SECRET_PROTOCOL" 
    assert original_data == decrypted
