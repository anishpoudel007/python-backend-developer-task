import threading

_thread_locals = threading.local()


def get_current_request():
    """
    Get the current request stored in thread-local storage
    """
    return getattr(_thread_locals, "request", None)


def get_client_ip(request):
    """
    Extract client IP address from request.

    Priority:
    1. X-Forwarded-For (first IP)
    2. REMOTE_ADDR
    """
    if request is None:
        return None

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # X-Forwarded-For may contain multiple IPs: client, proxy1, proxy2
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


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
