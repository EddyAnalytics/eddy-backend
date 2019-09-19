import django.db.models

import debezium_connectors.models
import experimental.dynamic_generation

model_dict = {name: cls for name, cls in debezium_connectors.models.__dict__.items() if
              isinstance(cls, type(django.db.models.Model))}
node_dict = {name: experimental.dynamic_generation.model_to_node(model) for name, model in model_dict.items()}
query_list = {experimental.dynamic_generation.model_to_query(model, node_dict[name]) for name, model in
              model_dict.items()}
mutation_list = {experimental.dynamic_generation.model_to_mutation(model, node_dict[name]) for name, model in
                 model_dict.items()}
