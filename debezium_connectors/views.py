from django.views import generic

# Create your views here.
from debezium_connectors.models import DebeziumConnector


class DebeziumConnectorListView(generic.ListView):
    model = DebeziumConnector
    context_object_name = 'debezium_connector_list'


class DebeziumConnectorDetailView(generic.DetailView):
    model = DebeziumConnector
    context_object_name = 'debezium_connector'
