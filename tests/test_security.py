from apps.api.core.security import hash_password, verify_password


def test_hash_password_verifies_correct_password():
    password = "mysecretpassword"
    
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True
    
    
def test_hash_password_fails_incorrect_password():
    password = "mysecretpassword"
    wrong = "totally-different-password"

    hashed = hash_password(password)
    
    assert verify_password(wrong, hashed) is False