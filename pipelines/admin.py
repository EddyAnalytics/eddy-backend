from django.contrib import admin

from pipelines.models import BlockType, Pipeline, Block

admin.site.register(Pipeline)
admin.site.register(Block)
admin.site.register(BlockType)
