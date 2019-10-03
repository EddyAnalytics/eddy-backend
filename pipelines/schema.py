import django.db.models
import graphene

import eddy_backend.celery
import pipelines.models
import utils.dynamic_generation

model_dict = {name: cls for name, cls in pipelines.models.__dict__.items() if
              isinstance(cls, type(django.db.models.Model)) and cls.__module__ == pipelines.models.__name__}
type__dict = {name: utils.dynamic_generation.model_to_type_(model) for name, model in model_dict.items()}
query_list = [utils.dynamic_generation.model_to_query(model, type__dict[name]) for name, model in
              model_dict.items()]
mutation_list = [utils.dynamic_generation.model_to_mutation(model, type__dict[name]) for name, model in
                 model_dict.items()]


# TODO temporary redis testing code
class SendCeleryTask(graphene.Mutation):
    class Arguments:
        input_topic = graphene.String(required=True)
        sql_query = graphene.String(required=True)
        output_topic = graphene.String(required=True)
        in_schema = graphene.String(required=True)
        out_schema = graphene.String(required=True)

    ok = graphene.Int()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        eddy_backend.celery.app.send_task('app.submit_flink_sql', (
            kwargs.get('input_topic'), kwargs.get('output_topic'), kwargs.get('sql_query'), kwargs.get('in_schema'), kwargs.get('out_schema')))
        return SendCeleryTask(ok=0)


class SendCeleryTaskMutation(object):
    send_celery_task = SendCeleryTask.Field()
