from django.contrib import admin

from dashboards.models import Dashboard, Widget, WidgetType

admin.site.register(Dashboard)
admin.site.register(Widget)
admin.site.register(WidgetType)
