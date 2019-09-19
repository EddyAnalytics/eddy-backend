import django.db.models

import debezium_connectors.models
import experimental.dynamic_generation
import experimental.old_schema

model_dict = {name: cls for name, cls in debezium_connectors.models.__dict__.items() if
              isinstance(cls, type(django.db.models.Model))}
print(model_dict)
node_dict = {name: experimental.dynamic_generation.model_to_node(model) for name, model in model_dict.items()}
print(node_dict)
query_list = {experimental.dynamic_generation.model_to_query(model, node_dict[name]) for name, model in
              model_dict.items()}
print(query_list)
mutation_list = {experimental.dynamic_generation.model_to_mutation(model, node_dict[name]) for name, model in
                 model_dict.items()}
print(mutation_list)

print('')

print(debezium_connectors.models.DebeziumConnector)
print(experimental.old_schema.DebeziumConnectorNode)
print(experimental.old_schema.DebeziumConnectorQuery)
print(experimental.old_schema.DebeziumConnectorMutation)
