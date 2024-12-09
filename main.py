import logging

from models import find_all_artists, find_artist, find_all_vouchers, \
    find_voucher, find_all_accounts, find_visitor, find_all_visitors, \
    Artist, Voucher, Account, Visitor, Credentials, AllowedStyles, \
    write_visitor, write_artist, write_voucher, write_account, \
    create_voucher, remove_voucher, create_account, remove_account, \
    create_session, remove_session

rootLogger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

fileHandler = logging.FileHandler("log.log")
consoleHandler = logging.StreamHandler()

rootLogger.addHandler(fileHandler)
rootLogger.addHandler(consoleHandler)

from fastapi import FastAPI, Query, Path

app = FastAPI(
    title="Картины на заказ",
    description="Посетители создают заказ, художники его выполняют"
)
from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_status():
    return {"status": "healthy"}


@app.get("/")
async def read_root():
    return get_status()


from typing import List, Optional, Literal

sessions_db = []
# Пример базы данных
artists_db = [
    Artist(login='artist1', id=1, style='realism'),
    Artist(login='artist2', id=2, style='impressionism'),
    Artist(login='artist3', id=3, style='modern'),
]
vouchers_db = [
    Voucher(id=1, customer='visitor1', executor='artist1', amount_pictures=3, price=100,
            description="3 pictures for 100$", status='placed', style='realism'),
    Voucher(id=2, customer='visitor2', executor='artist2', amount_pictures=5, price=200,
            description="5 pictures for 200$", status='in work', style='impressionism'),
    Voucher(id=3, customer='visitor3', executor='artist3', amount_pictures=2, price=150,
            description="2 pictures for 150$", status='ready', style='modern'),
    Voucher(id=4, customer='visitor2', executor='artist2', amount_pictures=5, price=200,
            description="5 pictures for 200$", status='in work', style='impressionism'),
    Voucher(id=5, customer='visitor2', executor='artist2', amount_pictures=5, price=200,
            description="5 pictures for 200$", status='in work', style='impressionism'),
]
accounts_db = [
    Account(login='artist1', password='password123', surName='Smith', firstName='Alice', patronymic='Marie',
            email='alice@email.com', type_role='artist', phone='1234567890', sex='f', date_of_birth='1995-05-15'),
    Account(login='artist2', password='password456', surName='Johnson', firstName='Bob', patronymic='Marie',
            email='bob@email.com', type_role='artist', phone='0987654321', sex='m', date_of_birth='1990-10-10'),
    Account(login='artist3', password='password123', surName='Dean', firstName='Amelia', patronymic='Marie',
            email='amelia@email.com', type_role='artist', phone='1234567890', sex='f', date_of_birth='1995-05-15'),
    Account(login='visitor1', password='password456', surName='Black', firstName='Adam', patronymic='Marie',
            email='adam@email.com', type_role='visitor', phone='0987654321', sex='m', date_of_birth='1990-10-10'),
    Account(login='visitor2', password='password123', surName='Fisher', firstName='Lily', patronymic='Marie',
            email='lily@email.com', type_role='visitor', phone='1234567890', sex='f', date_of_birth='1995-05-15'),
    Account(login='visitor3', password='password456', surName='Gate', firstName='Artur', patronymic='Marie',
            email='artur@email.com', type_role='visitor', phone='0987654321', sex='m', date_of_birth='1990-10-10'),
]
visitors_db = [
    Visitor(login='visitor1', id=1, residence='Moscow, Red Square'),
    Visitor(login='visitor2', id=2, residence='Saint Petersburg, Nevsky Prospect'),
    Visitor(login='visitor3', id=3, residence='Yaroslavl, st/ Syrkova'),
]


@app.put("/Artists", response_model=Artist, tags=["Artists"])
async def update_artist(
        new_style: AllowedStyles,
        session_id: str
):
    return write_artist(session_id, new_style)


@app.get("/Artists/list/", response_model=List[Artist], tags=["Artists"])
async def get_artists_list(
        session_id: str,
        style_list: Optional[List[str]] = Query(
            default=None,
            description="Style values that need to be considered for filter",
            enum=[
                "realism",
                "impressionism",
                "fauvism",
                "modern",
                "expressionism",
                "cubism",
                "futurism",
                "abstractionism",
                "dadaism",
                "pop-art"
            ],
            title="Style"
        ),
):
    return find_all_artists(session_id, style_list)


@app.get("/Artists/", response_model=Artist, tags=["Artists"])
async def get_artist(
        session_id: str,
        artist_id: int = Path(..., description="ID of Artists to return")
):
    return find_artist(session_id, artist_id)


@app.post("/Vouchers", response_model=Voucher, tags=["Vouchers"])
async def place_voucher(
        session_id: str,
        voucher: Voucher
):
    return create_voucher(session_id, voucher)


@app.get("/Vouchers/list", response_model=List[Voucher], tags=["Vouchers"])
async def find_vouchers(
        session_id: str,
        style: Optional[List[str]] = Query(
            default=None,
            description="Style values that need to be considered for filter",
            enum=[
                "realism",
                "impressionism",
                "fauvism",
                "modern",
                "expressionism",
                "cubism",
                "futurism",
                "abstractionism",
                "dadaism",
                "pop-art"
            ],
            title="Style"
        ),
        status: Optional[List[str]] = Query(
            default=None,
            description="Status values that need to be considered for filter",
            enum=[
                "placed",
                "in work",
                "ready"
            ],
            title="Status"
        )
):
    return find_all_vouchers(session_id, style, status)


@app.get("/Vouchers", response_model=Voucher, tags=["Vouchers"])
async def get_voucher(
        session_id: str,
        voucher_id: int = Path(..., description="ID of Vouchers to return")
):
    return find_voucher(session_id, voucher_id)


AllowedStatus = Literal[
    "placed",
    "in work",
    "ready"
]


@app.put("/Vouchers", response_model=Voucher, tags=["Vouchers"])
async def update_voucher(
        session_id: str,
        voucher_id: int,
        new_status: AllowedStatus
):
    return write_voucher(session_id, voucher_id, new_status)


@app.delete("/Vouchers", tags=["Vouchers"])
async def delete_voucher(
        session_id: str,
        voucher_id: int
):
    remove_voucher(session_id, voucher_id)
    return {"detail": "Vouchers deleted successfully"}


@app.post("/Accounts", response_model=Account, tags=["Accounts"])
async def place_account(
        account: Account,
):
    return create_account(account)


from fastapi.responses import JSONResponse


@app.post("/Accounts/log_in", tags=["Accounts"])
async def log_in(
        credentials: Credentials
):
    session_id = create_session(credentials)
    rootLogger.debug(f"session_id: `{session_id}`, login: `{credentials.login}`")
    content = {
        "message": "Login successful",
        "session_id": session_id
    }
    response = JSONResponse(content=content)
    return response


@app.delete("/Accounts/log_out", tags=["Accounts"])
async def log_out(
        session_id: str = ''
):
    remove_session(session_id)
    content = {"message": "Logout successful"}
    response = JSONResponse(content=content)
    return response


@app.get("/Accounts/list", response_model=List[Account], tags=["Accounts"])
async def find_accounts(
        session_id: str = Query(description="Working session id"),
        first_name: Optional[str] = Query(None, description="The first name to search for."),
        last_name: Optional[str] = Query(None, description="The last name to search for."),
):
    return find_all_accounts(session_id, first_name, last_name)


@app.put("/Accounts", tags=["Accounts"])
async def update_account_name(
        session_id: str,
        new_first_name: str = Query(..., description="New first name for the account"),
        new_last_name: str = Query(..., description="New last name for the account"),
):
    write_account(session_id, new_first_name, new_last_name)
    return {"message": "Account name updated successfully"}


@app.delete("/Accounts", tags=["Accounts"])
async def delete_account(
        session_id: str,
):
    remove_account(session_id)
    return {"message": "Account deleted successfully"}


@app.put("/Visitors", response_model=Visitor, tags=["Visitors"])
async def update_visitor(
        session_id: str,
        new_residence: str,
):
    return write_visitor(session_id, new_residence)


@app.get("/Visitors", response_model=Visitor, tags=["Visitors"])
async def get_visitor(
        session_id: str,
        visitor_id: int = Path(..., description="ID of Visitor to return"),
):
    return find_visitor(session_id, visitor_id)


@app.get("/Visitors/list", response_model=List[Visitor], tags=["Visitors"])
async def get_all_visitors(
        session_id: str,
):
    return find_all_visitors(session_id)


import strawberry
from strawberry.fastapi import GraphQLRouter


@strawberry.experimental.pydantic.type(model=Account, all_fields=True)
class AccountType:
    pass


@strawberry.experimental.pydantic.type(model=Visitor, all_fields=True)
class VisitorType:
    pass


@strawberry.experimental.pydantic.type(model=Artist, all_fields=True)
class ArtistType:
    pass


@strawberry.experimental.pydantic.type(model=Voucher, all_fields=True)
class VoucherType:
    pass


@strawberry.experimental.pydantic.type(model=Credentials, all_fields=True)
class CredentialsType:
    pass


@strawberry.type
class GraphQLQuery:
    @strawberry.field
    def accounts(
            self,
            session_id: str,
            first_name: str,
            last_name: str
    ) -> List[
        AccountType]:
        return find_all_accounts(session_id, first_name, last_name)

    @strawberry.field
    def visitor(self, session_id: str, visitor_id: int) -> VisitorType:
        return find_visitor(session_id, visitor_id)

    @strawberry.field
    def visitors(self, session_id: str) -> List[VisitorType]:
        return find_all_visitors(session_id)

    @strawberry.field
    def artist(self, session_id: str, artist_id: int) -> ArtistType:
        return find_artist(session_id, artist_id)

    @strawberry.field
    def artists(
            self,
            session_id: str,
            style_list: List[str]
    ) -> List[ArtistType]:
        return find_all_artists(session_id, style_list)

    @strawberry.field
    def voucher(self, session_id: str, voucher_id: int) -> VoucherType:
        return find_voucher(session_id, voucher_id)

    @strawberry.field
    def vouchers(
            self,
            session_id: str,
            style: List[str],
            status: List[str]
    ) -> List[VoucherType]:
        return find_all_vouchers(session_id, style, status)


@strawberry.type
class GraphQLMutation:
    @strawberry.mutation
    def add_account(
            self,
            account: AccountType,
    ) -> AccountType:
        new_account = Account(
            login=account.login,
            password=account.password,
            surName=account.surName,
            firstName=account.firstName,
            patronymic=account.patronymic,
            email=account.email,
            type_role=account.type_role,
            phone=account.phone,
            sex=account.sex,
            date_of_birth=account.date_of_birth
        )
        return create_account(new_account)

    @strawberry.mutation
    def update_account(
            self,
            session_id: str,
            new_first_name: str,
            new_last_name: str,
    ) -> str:
        return write_account(session_id, new_first_name, new_last_name)

    @strawberry.mutation
    async def delete_account(
            self,
            session_id: str,
    ) -> str:
        return remove_account(session_id)

    @strawberry.mutation
    def update_visitor(
            self, session_id: str,
            new_residence: str,
    ) -> VisitorType:
        return write_visitor(session_id, new_residence)

    @strawberry.mutation
    def update_artist(
            self, session_id: str,
            new_style: str,
    ) -> VisitorType:
        return write_artist(session_id, new_style)

    @strawberry.mutation
    def add_voucher(
            self, session_id: str,
            voucher: VoucherType,
    ) -> VoucherType:
        new_voucher = Voucher(
            amount_pictures=voucher.amount_pictures,
            price=voucher.price,
            description=voucher.description,
            style=voucher.style
        )
        return create_voucher(session_id, new_voucher)

    @strawberry.mutation
    def update_voucher(
            self,
            session_id: str,
            voucher_id: int,
            new_status: str,
    ) -> VoucherType:
        return write_voucher(session_id, voucher_id, new_status)

    @strawberry.mutation
    def delete_voucher(
            self,
            session_id: str,
            voucher_id: int,
    ) -> VoucherType:
        return remove_voucher(session_id, voucher_id)

    @strawberry.mutation
    def log_in(
            self,
            credentials_input: CredentialsType,
    ) -> str:
        credentials = Credentials(
            login=credentials_input.login,
            password=credentials_input.password
        )
        return create_session(credentials)

    @strawberry.mutation
    def log_out(
            self,
            session_id: Optional[str] = None,
    ) -> str:
        return remove_session(session_id)


schema = strawberry.Schema(GraphQLQuery, GraphQLMutation)

# schema = strawberry.Schema(GraphQLQuery)


graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
