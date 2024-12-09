import strawberry
from strawberry.fastapi import GraphQLRouter

from GqlMutation import GraphQLMutation
from GqlQuery import GraphQLQuery

schema = strawberry.Schema(GraphQLQuery, GraphQLMutation)

graphql_app = GraphQLRouter(schema)
