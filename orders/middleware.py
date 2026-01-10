import threading

_thread_locals = threading.local()


def get_current_request():
    """
    Get the current request stored in thread-local storage
    """
    return getattr(_thread_locals, "request", None)


class RequestMiddleware:
    """
    Middleware to store the current request in thread-local storage
    and clean it up after processing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request in thread-local storage
        _thread_locals.request = request

        try:
            response = self.get_response(request)
            return response
        finally:
            # Clean up the request after processing
            if hasattr(_thread_locals, "request"):
                del _thread_locals.request
