from .models import RequestLog
from .models import BlockedIP
from django.http import HttpResponseForbidden
from django.core.cache import cache

GEO_CACHE_SECONDS = 60 * 60 * 24  # 24 hours

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Getting client IP address
        ip_address = self.get_client_ip(request)

        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Forbidden: Your IP has been blocked.")

        # Logging request data
        RequestLog.objects.create(
            ip_address=ip_address,
            path=request.path
        )

        response = self.get_response(request)
        return response


    def get_geo(self, ip_address, request):
        """
        Returns (country, city) using a 24h cache.
        Tries to read request.geolocation if available.
        """
        cache_key = f"geo:{ip_address}"
        cached = cache.get(cache_key)
        if cached:
            return cached.get("country"), cached.get("city")

        country = None
        city = None

        # If django-ip-geolocation middleware is installed before this middleware,
        # it exposes request.geolocation :contentReference[oaicite:3]{index=3}
        geo = getattr(request, "geolocation", None)
        if geo:
            # Different backends may expose fields slightly differently,
            # so we do safe lookups.
            country = getattr(geo, "country", None) or getattr(geo, "_country", None)
            city = getattr(geo, "city", None) or getattr(geo, "_city", None)

            # country might be a dict (per library docs), so normalize
            if isinstance(country, dict):
                country = country.get("name") or country.get("code")

        cache.set(cache_key, {"country": country, "city": city}, timeout=GEO_CACHE_SECONDS)
        return country, city

    def get_client_ip(self, request):
        """
        Extracting client IP address, accounting for proxies.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
