from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.urls import path
from django.shortcuts import render
import plotly.graph_objects as go
from django.utils.timezone import now, timedelta
from .models import PageView

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'path', 'ip_address', 'browser', 'os', 'device', 'user')
    search_fields = ('path', 'ip_address', 'user_agent', 'browser', 'os')
    list_filter = ('browser', 'os', 'device')

    change_list_template = "pageview_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('stats/', self.admin_site.admin_view(self.stats_view), name='analytics_pageview_stats'),
        ]
        return custom_urls + urls

    def stats_view(self, request):
        thirty_days_ago = now() - timedelta(days=30)
        daily_data = (
            PageView.objects.filter(timestamp__gte=thirty_days_ago)
            .annotate(day=TruncDate('timestamp'))
            .values('day')
            .annotate(total=Count('id'))
            .order_by('day')
        )

        days = [d['day'].strftime('%d/%m') for d in daily_data]
        totals = [d['total'] for d in daily_data]

        fig_daily = go.Figure()
        fig_daily.add_trace(go.Scatter(
            x=days,
            y=totals,
            mode='lines+markers',
            name='Acessos por Dia'
        ))
        fig_daily.update_layout(
            title='📅 Acessos Diários',
            xaxis_title='Dia',
            yaxis_title='Visitas',
            template='plotly_white'
        )

        os_data = (
            PageView.objects
            .values('os')
            .annotate(total=Count('id'))
            .order_by('-total')[:10]
        )

        os_names = [o['os'] or 'Desconhecido' for o in os_data]
        os_counts = [o['total'] for o in os_data]

        fig_os = go.Figure([go.Bar(x=os_names, y=os_counts)])
        fig_os.update_layout(title='💻 Acessos por Sistema Operacional', template='plotly_white')

        browser_data = (
            PageView.objects
            .values('browser')
            .annotate(total=Count('id'))
            .order_by('-total')[:10]
        )

        browser_names = [b['browser'] or 'Desconhecido' for b in browser_data]
        browser_counts = [b['total'] for b in browser_data]

        fig_browser = go.Figure([go.Pie(labels=browser_names, values=browser_counts)])
        fig_browser.update_layout(title='🌐 Acessos por Navegador')

        context = {
            'title': 'Estatísticas de Acesso',
            'daily_chart': fig_daily.to_html(full_html=False),
            'os_chart': fig_os.to_html(full_html=False),
            'browser_chart': fig_browser.to_html(full_html=False),
        }
        return render(request, 'stats.html', context)
