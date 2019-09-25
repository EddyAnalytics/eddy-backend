import django.db.models

import experimental.dynamic_generation
import workspaces.models

model_dict = {name: cls for name, cls in workspaces.models.__dict__.items() if
              isinstance(cls, type(django.db.models.Model)) and cls.__module__ == workspaces.models.__name__}
type__dict = {name: experimental.dynamic_generation.model_to_type_(model) for name, model in model_dict.items()}
query_list = [experimental.dynamic_generation.model_to_query(model, type__dict[name]) for name, model in
              model_dict.items()]
mutation_list = [experimental.dynamic_generation.model_to_mutation(model, type__dict[name]) for name, model in
                 model_dict.items()]
