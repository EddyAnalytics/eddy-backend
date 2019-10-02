from django.db import models


class Pipeline(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='pipelines', on_delete=models.CASCADE)
    project = models.ForeignKey('workspaces.Project', related_name='pipelines', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)


class Block(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='blocks', on_delete=models.CASCADE)
    pipeline = models.ForeignKey('pipelines.Pipeline', related_name='blocks', on_delete=models.CASCADE)
    block_type = models.ForeignKey('pipelines.BlockType', related_name='blocks', on_delete=models.CASCADE)
    json_config = models.CharField(max_length=200)


class BlockType(models.Model):
    id = models.AutoField(primary_key=True)
    # block type does not need a reference to a user because they are usable by any user
    # TODO this probably causes issues with users requesting eachothers data probabbly removed related queries from block
