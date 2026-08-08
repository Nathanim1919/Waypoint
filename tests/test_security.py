from apps.api.core.security import create_refresh_token, hash_password, verify_password, create_access_token, decode_token


def test_hash_password_verifies_correct_password():
    password = "mysecretpassword"
    
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True
    
    
def test_hash_password_fails_incorrect_password():
    password = "mysecretpassword"
    wrong = "totally-different-password"

    hashed = hash_password(password)
    
    assert verify_password(wrong, hashed) is False
    
    
def test_hash_password_generates_different_hashes():
    password = "mysecretpassword"
    
    hashed1 = hash_password(password)
    hashed2 = hash_password(password)
    
    assert hashed1 != hashed2
    
    
def test_verify_password_with_empty_strings():
    assert verify_password("", "") is False
    assert verify_password("password", "") is False
    assert verify_password("", "hashed") is False
    
def test_verify_password_with_non_string_inputs():
    assert verify_password(None, None) is False
    assert verify_password("password", None) is False
    assert verify_password(None, "hashed") is False
    

def test_verify_password_with_invalid_hashed_password():
    password = "mysecretpassword"
    invalid_hashed = "not-a-valid-hash"
    
    assert verify_password(password, invalid_hashed) is False
    
    
def test_create_access_token_and_decode():
    subject = "user123"
    
    token = create_access_token(subject)
    
    decoded_token = decode_token(token)
    
    assert decoded_token["sub"] == subject
    
    
def test_access_token_and_refresh_token_have_different_types():
    subject = "user123"
    
    access_token = create_access_token(subject)
    refresh_token = create_refresh_token(subject, "userSessionId")  # Assuming you have a separate function for refresh
    
    decoded_access = decode_token(access_token)
    decoded_refresh = decode_token(refresh_token)
    
    assert decoded_access["type"] == "access"
    assert decoded_refresh["type"] == "refresh"
    assert decoded_access["type"] != decoded_refresh["type"]
    