import graphene
import graphql_jwt

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
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
