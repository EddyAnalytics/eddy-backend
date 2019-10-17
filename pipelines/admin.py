from django.contrib import admin

from pipelines.models import BlockType, Pipeline, Block
from utils.utils import ReadOnlyIdAdmin

admin.site.register(Pipeline, ReadOnlyIdAdmin)
admin.site.register(Block, ReadOnlyIdAdmin)
admin.site.register(BlockType, ReadOnlyIdAdmin)
