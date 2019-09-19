import graphene

import debezium_connectors.schema

RootQuery = type(
    'RootQuery',
    tuple(debezium_connectors.schema.query_list),
    {}
)

RootMutation = type(
    'RootMutation',
    tuple(debezium_connectors.schema.mutation_list),
    {}
)


class Query(RootQuery, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass


class Mutation(RootMutation, graphene.ObjectType):
    # This class will inherit from multiple Mutations
    # as we begin to add more apps to our project
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
