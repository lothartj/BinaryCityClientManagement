from .viewssendnoti import _thread_locals

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response 