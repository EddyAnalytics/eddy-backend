from django.contrib import admin

from dashboards.models import Dashboard, Widget, WidgetType
from utils.utils import ReadOnlyIdAdmin

admin.site.register(Dashboard, ReadOnlyIdAdmin)
admin.site.register(Widget, ReadOnlyIdAdmin)
admin.site.register(WidgetType, ReadOnlyIdAdmin)
