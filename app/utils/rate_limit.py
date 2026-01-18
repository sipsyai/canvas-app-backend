"""Rate limiting configuration using SlowAPI"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Create limiter instance
# Uses client IP address as the key for rate limiting
limiter = Limiter(key_func=get_remote_address)
