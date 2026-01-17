from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ratelimit.decorators import ratelimit


def login_rate(group, request):
    """
    Dynamic rate:
    - authenticated: 10 requests per minute
    - anonymous: 5 requests per minute
    """
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        return "10/m"
    return "5/m"


@require_POST
@ratelimit(key="ip", rate=login_rate, block=True)
def login_view(request):
    """
    Example sensitive endpoint protected by rate limiting.
    Replace the body with your real login logic later (JWT/session/etc).
    """
    return JsonResponse({"message": "Login endpoint (rate-limited)."})

