from .viewssendnoti import _thread_locals
from .viewsappaccessed import track_app_access
import re

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response

class AppAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.static_pattern = re.compile(r'^/static/')
        self.admin_pattern = re.compile(r'^/admin/')
        self.api_pattern = re.compile(r'^/api/')
        self.excluded_patterns = [
            self.static_pattern,
            self.admin_pattern,
            self.api_pattern,
        ]

    def __call__(self, request):
        path = request.path
        if any(pattern.match(path) for pattern in self.excluded_patterns):
            return self.get_response(request)
        if path in ['/favicon.ico', '/robots.txt']:
            return self.get_response(request)
        if path == '/':
            track_app_access(request)
        response = self.get_response(request)
        return response 