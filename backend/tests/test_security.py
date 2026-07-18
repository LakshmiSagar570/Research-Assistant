import unittest

from app.core.security import hash_password, verify_password


class SecurityTests(unittest.TestCase):
    def test_password_roundtrip(self):
        password = "demo1234"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrong-password", hashed))


if __name__ == "__main__":
    unittest.main()
