import django.db.models

import debezium_connectors
import test.old_schema
from debezium_connectors.models import DebeziumConnectorConfig
from test.dymanic_generation import model_to_node, model_to_query, model_to_mutation

model_dict = {name: cls for name, cls in debezium_connectors.models.__dict__.items() if
              isinstance(cls, type(django.db.models.Model))}
print(model_dict)
node_dict = {name: model_to_node(model) for name, model in model_dict.items()}
print(node_dict)
query_list = {model_to_query(model, node_dict[name]) for name, model in model_dict.items()}
print(query_list)
mutation_list = {model_to_mutation(model, node_dict[name]) for name, model in model_dict.items()}
print(mutation_list)

print('')

print(debezium_connectors.models.DebeziumConnector)
print(test.old_schema.DebeziumConnectorNode)
print(test.old_schema.DebeziumConnectorQuery)
print(test.old_schema.DebeziumConnectorMutation)
