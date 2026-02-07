"""
Middleware: show "Coming Soon" landing page unless user is logged in as staff.
Staff can see the full site and access /admin/ to log in.
"""

from django.shortcuts import render


class ComingSoonMiddleware:
    """Show Coming Soon page to non-staff visitors; staff see full site."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Allow admin (login, logout, etc.), static, media
        if path.startswith('/admin/') or path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        # Allow staff to see full site
        if request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)

        return render(request, 'core/coming_soon.html')
