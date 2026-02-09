"""
Alternative WSGI entry point for compatibility with some hosting platforms.
"""

from truck_platform.wsgi import application

# Make application available as both 'app' and 'application'
app = application