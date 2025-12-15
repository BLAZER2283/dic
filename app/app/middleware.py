from django.utils.deprecation import MiddlewareMixin


class DisableCSRFMiddleware(MiddlewareMixin):

    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Disable CSRF for API paths
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
