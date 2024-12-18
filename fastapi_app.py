from fastapi import Query, Path, FastAPI, Request

from models import find_all_artists, find_artist, find_all_vouchers, \
    find_voucher, find_all_accounts, find_visitor, find_all_visitors, \
    Artist, Voucher, Account, Visitor, Credentials, AllowedStyles, \
    write_visitor, write_artist, write_voucher, write_account, \
    create_voucher, remove_voucher, create_account, remove_account, \
    create_session, remove_session, my_login_and_role, my_account, \
    find_artist_style, find_all_styles, find_account, NewAccount

app = FastAPI(
    title="Картины на заказ",
    description="Посетители создают заказ, художники его выполняют"
)


@app.get("/")
async def read_root():
    return {"status": "healthy"}


from typing import List, Optional, Literal


@app.put("/Artists", response_model=Artist, tags=["Artists"])
async def update_artist(
        new_style: AllowedStyles,
        session_id: str
):
    return write_artist(session_id, new_style)


@app.get("/Artists/list/", response_model=List[Artist], tags=["Artists"])
async def get_artists_list(
        request: Request,
        session_id: Optional[str] = None,
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
    if session_id is None:
        session_id = extract_bearer(request)

    return find_all_artists(session_id, style_list)


@app.get("/Artists/", response_model=Artist, tags=["Artists"])
async def get_artist(
        session_id: str,
        artist_id: int = Path(..., description="ID of Artists to return")
):
    return find_artist(session_id, artist_id)


@app.get(
    "/Artists/styles/",
    tags=["Artists"]
)
async def get_all_styles():
    return {"styles": find_all_styles()}


@app.get(
    "/Artists/{login}/styles/",
    tags=["Artists"]
)
async def get_artist_style(
        request: Request,
        login: str,
):
    token = extract_bearer(request)

    return {"styles": find_artist_style(token, login)}


@app.post("/Vouchers", response_model=Voucher, tags=["Vouchers"])
async def place_voucher(
        request: Request,
        voucher: Voucher,
        session_id: Optional[str] = None,
):
    if session_id is None:
        session_id = extract_bearer(request)
    return create_voucher(session_id, voucher)


@app.get("/Vouchers/list", response_model=List[Voucher], tags=["Vouchers"])
async def find_vouchers(
        request: Request,
        session_id: Optional[str] = None,
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
    if session_id is None:
        session_id = extract_bearer(request)
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
        account: NewAccount,
):
    return create_account(account)


from fastapi.responses import JSONResponse


@app.post("/Accounts/log_in", tags=["Accounts"])
async def log_in(
        credentials: Credentials
):
    session_id = create_session(credentials)
    content = {
        "message": "Login successful",
        "session_id": session_id
    }
    response = JSONResponse(content=content)
    return response


@app.get("/Accounts/me/", tags=["Accounts"])
async def me(request: Request):
    token = extract_bearer(request)
    content = my_login_and_role(token)

    response = JSONResponse(content=content)

    return response


@app.get("/Accounts/me/about/", tags=["Accounts"])
async def about_me(request: Request):
    token = extract_bearer(request)
    account = my_account(token)

    content = {
        "id": account.id,
        "username": account.login,
        "first_name": account.firstName,
        "last_name": account.surName,
        "middle_name": account.patronymic,
        "birth_date": account.date_of_birth,
        "phone_number": account.phone,
        "email": account.email,
        "gender": account.sex,
        "role": account.type_role,
        "adres": account.residence or "",  # Если адрес пустой, возвращаем пустую строку
        "avatar_url": "",  # Возвращаем URL аватарки, если оно есть
    }

    response = JSONResponse(content=content)

    return response


@app.get("/Accounts/show/", tags=["Accounts"])
async def show_account(
        login: str = Query(description="username"),
):
    account = find_account(login)

    content = {
        "id": account.id,
        "username": account.login,
        "first_name": account.firstName,
        "last_name": account.surName,
        "middle_name": account.patronymic,
        "birth_date": account.date_of_birth,
        "phone_number": account.phone,
        "email": account.email,
        "gender": account.sex,
        "role": account.type_role,
        # Если адрес пустой, возвращаем пустую строку
        "adres": account.residence or "",
        "avatar_url": "",
    }

    response = JSONResponse(content=content)

    return response


def extract_bearer(request) -> str:
    headers = request.headers
    bearer = headers.get('Authorization')  # Bearer YourTokenHere
    token = bearer.split()[1]  # YourTokenHere
    return str(token)


@app.delete("/Accounts/log_out", tags=["Accounts"])
async def log_out(
        request: Request,
        session_id: Optional[str] = None
):
    if session_id is None:
        session_id = extract_bearer(request)
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
        request: Request,
        session_id: Optional[str] = None,
        new_first_name: str = Query(..., description="New first name for the account"),
        new_last_name: str = Query(..., description="New last name for the account"),
):
    if session_id is None:
        session_id = extract_bearer(request)
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
        request: Request,
        new_residence: str,
        session_id: Optional[str] = None,
):
    if session_id is None:
        session_id = extract_bearer(request)
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
