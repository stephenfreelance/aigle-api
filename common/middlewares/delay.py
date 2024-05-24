import os
from django.utils.deprecation import MiddlewareMixin
import time


class DelayMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.extra_delay = int(os.environ.get("EXTRA_DELAY_REQUEST", "0"))

    def process_request(self, request):
        # This method is called before the view
        # You can modify the request here
        return None

    def process_response(self, request, response):
        # This method is called after the view
        # You can modify the response here
        time.sleep(self.extra_delay)
        return response
