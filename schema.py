import graphene

import debezium_connectors.schema


class Query(debezium_connectors.schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass


schema = graphene.Schema(query=Query)