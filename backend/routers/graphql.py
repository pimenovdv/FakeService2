import strawberry
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class User:
    id: int
    name: str
    email: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> User | None:
        if id == 1:
            return User(id=1, name="John Doe", email="john@example.com")
        return None

schema = strawberry.Schema(query=Query)
router = GraphQLRouter(schema, path="/graphql")
