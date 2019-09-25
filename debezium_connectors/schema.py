import django.db.models

import debezium_connectors.models
import utils.dynamic_generation

model_dict = {name: cls for name, cls in debezium_connectors.models.__dict__.items() if
              isinstance(cls, type(django.db.models.Model)) and cls.__module__ == debezium_connectors.models.__name__}
type__dict = {name: utils.dynamic_generation.model_to_type_(model) for name, model in model_dict.items()}
query_list = [utils.dynamic_generation.model_to_query(model, type__dict[name]) for name, model in
              model_dict.items()]
mutation_list = [utils.dynamic_generation.model_to_mutation(model, type__dict[name]) for name, model in
                 model_dict.items()]
