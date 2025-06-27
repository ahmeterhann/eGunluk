import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        method = request.method
        path = request.get_full_path()

        logger.info(f"HTTP {method} request to {path} by {user}")

        response = self.get_response(request)
        return response