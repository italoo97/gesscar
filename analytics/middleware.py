from .models import PageView
from django.utils.deprecation import MiddlewareMixin
from user_agents import parse

class AnalyticsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if any([
            request.path.startswith('/static/'),
            request.path.startswith('/media/'),
            request.path.startswith('/admin/'),
            request.path.startswith('/api/'),
            request.method != 'GET'
        ]):
            return None

        ip = self.get_client_ip(request)
        ua_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(ua_string)

        # Captura as infos principais
        pv = PageView(
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip,
            path=request.path,
            referrer=request.META.get('HTTP_REFERER'),
            user_agent=ua_string,
            browser=f"{user_agent.browser.family} {user_agent.browser.version_string}",
            os=f"{user_agent.os.family} {user_agent.os.version_string}",
            device=user_agent.device.family,
            language=request.META.get('HTTP_ACCEPT_LANGUAGE'),
            session_key=request.session.session_key
        )
        pv.save()

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
