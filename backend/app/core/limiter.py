"""
Shared slowapi Limiter instance.

Kept in its own module (not main.py) so routers can import it without
creating a circular import (main.py imports routers, routers would
otherwise need to import back from main.py).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
