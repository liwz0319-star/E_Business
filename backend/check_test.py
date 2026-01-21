"""Quick test to check auth functionality."""
import sys
sys.path.insert(0, '.')

from app.core.security import get_password_hash, verify_password

# Test 1: Hash password
password = "securepassword123"
hashed = get_password_hash(password)
print(f"Test 1 - Hash password:")
print(f"  Password: {password}")
print(f"  Hash: {hashed[:50]}...")
print(f"  Starts with $5$: {hashed.startswith('$5$')}")
print(f"  Length > 50: {len(hashed) > 50}")

# Test 2: Verify correct password
result = verify_password(password, hashed)
print(f"\nTest 2 - Verify correct password: {result}")

# Test 3: Verify wrong password
result = verify_password("wrongpassword", hashed)
print(f"Test 3 - Verify wrong password: {result}")

print("\nAll basic tests completed!")
