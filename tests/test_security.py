from taskforge.security import (
    generate_token,
    hash_password,
    hash_token,
    verify_password,
    verify_token,
)


def test_password_hash_verifies_password_without_storing_plaintext() -> None:
    stored_hash = hash_password("correct horse battery staple")

    assert stored_hash != "correct horse battery staple"
    assert verify_password("correct horse battery staple", stored_hash)
    assert not verify_password("wrong password", stored_hash)


def test_generated_tokens_are_random_and_hash_verifiable() -> None:
    first = generate_token()
    second = generate_token()

    assert first != second
    assert len(first) >= 32

    stored_hash = hash_token(first)

    assert stored_hash != first
    assert verify_token(first, stored_hash)
    assert not verify_token(second, stored_hash)
