from fastapi.middleware.cors import CORSMiddleware

from fastapi_app import *
from gql_app import graphql_app

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_app, prefix="/graphql")
