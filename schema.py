import graphene
import graphql_jwt

import authentication.schema
import integrations.schema
import pipelines.schema
import projects.schema
import workspaces.schema

RootQuery = type(
    'RootQuery',
    tuple(
        authentication.schema.query_list + integrations.schema.query_list + pipelines.schema.query_list + projects.schema.query_list + workspaces.schema.query_list
    ),
    {}
)

RootMutation = type(
    'RootMutation',
    tuple(
        authentication.schema.mutation_list + integrations.schema.mutation_list + pipelines.schema.mutation_list + projects.schema.mutation_list + workspaces.schema.mutation_list
    ),
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
