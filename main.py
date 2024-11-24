import logging
from typing import List, Optional, Literal, get_args

from fastapi import FastAPI, HTTPException, Query, Path, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

rootLogger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

fileHandler = logging.FileHandler("log.log")
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()

rootLogger.addHandler(consoleHandler)


def connect_db():
    """
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="root",
                                    host="127.0.0.1",
                                    port="5433",
                                    database="fias")

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        rootLogger.info("Connection established")

    except (Exception, psycopg2.Error) as error :
        print("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                ##print("PostgreSQL connection is closed")
                rootLogger.info("PostgreSQL connection is closed")
    """


app = FastAPI(title="Картины на заказ",
              description="Посетители создают заказ, художники его выполняют")

from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {
        "Api-web-client-address": "http://127.0.0.1:8001/docs"
    }


class Voucher(BaseModel):
    id: int = Field(..., example=10)
    customer: str = Field(..., example="198login")
    executor: str = Field(..., example="198login")
    amount_pictures: int = Field(..., example=3)
    price: int = Field(..., example=100)
    description: str = Field(..., example="3 pictures for 100$")
    status: Literal['placed', 'in work', 'ready'] = Field(..., example='placed')
    style: Literal[
        'realism', 'impressionism', 'fauvism', 'modern',
        'expressionism', 'cubism', 'futurism', 'abstractionism',
        'dadaism', 'pop-art'
    ] = Field(..., example='realism')


class Account(BaseModel):
    login: str = Field(..., example='10')
    password: str = Field(..., example='theAccounts')
    surName: str = Field(..., example='Green')
    firstName: str = Field(..., example='John')
    patronymic: Optional[str] = Field(None, example='James')
    email: str = Field(..., example='john@email.com')
    type_role: str = Field(..., example='artist')
    phone: str = Field(..., example='12345')
    sex: Literal['f', 'm'] = Field(..., example='m')
    date_of_birth: str = Field(..., example='2000-01-01')  # формат даты


class Visitor(BaseModel):
    login: str = Field(..., example='10')
    id: int = Field(..., example=10)
    residence: str = Field(..., example='Yaroslavl, st/ Syrkova')


class Artist(BaseModel):
    login: str = Field(..., example='10')
    id: int = Field(..., example=10)
    style: Literal[
        'realism', 'impressionism', 'fauvism', 'modern',
        'expressionism', 'cubism', 'futurism', 'abstractionism',
        'dadaism', 'pop-art'
    ] = Field(..., example='realism')


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


def api_key():
    return "api_key"


def artist_vouchers_auth():
    return ["write:Artists", "read:Artists", "write:Visitors", "read:Visitors"]


AllowedStyles = Literal[
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
]


@app.put("/Artists", response_model=Artist, tags=["Artists"])
async def update_artist(
        request: Request,
        new_style: AllowedStyles
):
    login = request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    connect_db()
    # Ищем артиста по login

    existing_artist = next((artist for artist in artists_db if artist.login == login), None)

    if existing_artist is None:
        raise HTTPException(status_code=404, detail="Denied, you are not artist")

    # Обновляем место жительства
    existing_artist.style = new_style
    return existing_artist


@app.get("/Artists", response_model=List[Artist], tags=["Artists"])
async def find_artists_by_style(
        request: Request,
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
        )
):
    login = request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    connect_db()
    existing_styles = list()
    if style_list is not None:
        existing_style = next((style_item for style_item in style_list if style_item in AllowedStyles), None)

        existing_styles = list(set(style_list) & set(get_args(AllowedStyles)))

    if style_list is not None and not existing_styles:
        raise HTTPException(status_code=400, detail="Style not found in AllowedStyles")

    # Если стиль не указан, возвращаем всех артистов
    if style_list is None:
        filtered_artists = artists_db
    else:
        # Фильтруем артистов на основе предоставленных стилей
        filtered_artists = [artist for artist in artists_db if artist.style in style_list]

    if not filtered_artists:
        raise HTTPException(status_code=404, detail="Artists with such style not found")

    return filtered_artists


@app.get("/Artists/{artist_id}", response_model=Artist, tags=["Artists"])
async def get_artist_by_id(
        request: Request,
        artist_id: int = Path(..., description="ID of Artists to return")
):
    login = request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    connect_db()
    artist = next((artist for artist in artists_db if artist.id == artist_id), None)
    ##artist = next((artist for artist in artists_db if artist.login == login), None)

    if artist is None:
        raise HTTPException(status_code=404, detail="Artists not found")

    return artist


#####################################################################################


@app.post("/Vouchers", response_model=Voucher, tags=["Vouchers"])
async def place_vouchers(
        request: Request,
        voucher: Voucher
):
    # Получаем логин из куки
    login = request.cookies.get('login')

    # Проверяем, что логин существует и не пустой
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    connect_db()
    # Ищем посетителя по ID
    existing_visitor = next((visitor for visitor in visitors_db if visitor.login == login), None)

    if existing_visitor is None:
        raise HTTPException(status_code=404, detail="Visitor not found")

    # Получаем максимальный ID для нового ваучера
    max_id = max((v.id for v in vouchers_db), default=0)

    # Создаем новый предзаказ
    new_voucher = Voucher(
        id=max_id + 1,
        customer=login,  # Используем логин из куки
        executor="",
        amount_pictures=voucher.amount_pictures,
        price=voucher.price,
        description=voucher.description,
        status="placed",
        style=voucher.style
    )

    # Добавляем новый предзаказ в базу данных
    vouchers_db.append(new_voucher)

    return new_voucher


@app.get("/Vouchers", response_model=List[Voucher], tags=["Vouchers"])
async def find_vouchers(
        request: Request,
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
    # Получаем логин из куки
    login = request.cookies.get('login')

    # Проверяем, что логин существует и не пустой
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    connect_db()
    if not vouchers_db:
        raise HTTPException(status_code=404, detail="Vouchers not exists, please add someone")
    # Если ни стиль, ни статус не указаны, возвращаем все ваучеры
    if style is None and status is None:
        return vouchers_db

    # Фильтруем ваучеры по стилю и статусу

    filtered_vouchers = [
        voucher for voucher in vouchers_db
        if (
                ((style is None) or (style is not None and voucher.style in style))
                and
                ((status is None) or (status is not None and voucher.status in status))

        )
    ]

    # Проверяем, есть ли отфильтрованные ваучеры
    if not filtered_vouchers:
        raise HTTPException(status_code=404, detail="Vouchers not found")

    return filtered_vouchers


@app.get("/Vouchers/{voucher_id}", response_model=Voucher, tags=["Vouchers"])
async def get_vouchers_by_id(
        request: Request,
        voucher_id: int = Path(..., description="ID of Vouchers to return")
):
    # Получаем логин из куки
    login = request.cookies.get('login')

    # Проверяем, что логин существует и не пустой
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    connect_db()
    voucher = next((v for v in vouchers_db if v.id == voucher_id), None)

    if voucher is None:
        raise HTTPException(status_code=404, detail="Voucher not found")

    return voucher


AllowedStatus = Literal[
    "placed",
    "in work",
    "ready"
]


@app.put("/Vouchers", response_model=Voucher, tags=["Vouchers"])
async def update_voucher(
        request: Request,
        voucher_id: int,
        new_status: AllowedStatus
):
    login = request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    connect_db()
    # Ищем художника по login
    existing_artist = next((artist for artist in artists_db if artist.login == login), None)

    if existing_artist is None:
        raise HTTPException(status_code=404, detail="Denied, you are not artist")

    # Ищем ваучер
    existing_voucher = next((v for v in vouchers_db if v.id == voucher_id), None)

    if existing_voucher is None:
        raise HTTPException(status_code=404, detail="Voucher not found")

    if (existing_voucher.status != 'placed' and existing_voucher.executor != login):
        raise HTTPException(status_code=403, detail="Access denied: You do not own this voucher record")

    if (existing_voucher.status == 'placed' and existing_voucher.executor == ""):
        existing_voucher.executor = login

    existing_voucher.status = new_status  # Обновляем только статус
    return existing_voucher


@app.delete("/Vouchers/{vouchers_id}", tags=["Vouchers"])
async def delete_voucher(
        request: Request,
        vouchers_id: int
):
    login = request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    connect_db()
    # Ищем посетителя по ID
    existing_visitor = next((visitor for visitor in visitors_db if visitor.login == login), None)

    if existing_visitor is None:
        raise HTTPException(status_code=404, detail="Denied, you are not visitor")

    # Проверяем, что логин пользователя совпадает с владельцем записи
    if existing_visitor.login != login:
        raise HTTPException(status_code=403, detail="Access denied: You do not own this voucher")

    # Находим индекс ваучера с указанным идентификатором
    voucher_index = next((index for index, voucher in enumerate(vouchers_db) if voucher.id == vouchers_id), None)

    # Если ваучер не найден, возвращаем 404
    if voucher_index is None:
        raise HTTPException(status_code=404, detail="Voucher not found")

    # Удаляем ваучер из базы данных
    vouchers_db.pop(voucher_index)

    return {"detail": "Vouchers deleted successfully"}


######################################################################################################


AllowedRols = Literal[
    "visitor",
    "artist"
]


@app.post("/Accounts", response_model=Account, tags=["Accounts"])
async def place_accounts(
        account: Account,
):
    if any(v.login == account.login for v in accounts_db):
        raise HTTPException(status_code=400, detail="Error login already exists.")

    # Создаем новый 
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

    if (account.type_role == "artist"):
        new_artist = Artist(
            id=max((voucher.id for voucher in artists_db), default=0) + 1,
            login=account.login,
            style="realism"
        )
        artists_db.append(new_artist)

    if (account.type_role == "visitor"):
        new_visitor = Visitor(
            id=max((voucher.id for voucher in visitors_db), default=0) + 1,
            login=account.login,
            residence="None"
        )
        visitors_db.append(new_visitor)

    connect_db()
    # Добавляем новый предзаказ в базу данных
    accounts_db.append(new_account)

    return new_account


# Имитация хранилища для текущего пользователя (для примера)
current_user = None


class Credentials(BaseModel):
    login: str = Field(..., example='login')
    password: str = Field(..., example='password')


class Cookies(BaseModel):
    login: str | None = None


@app.post("/Accounts/login", tags=["Accounts"])
async def login(
        credentials: Credentials
):
    connect_db()
    for account in accounts_db:
        if account.login == credentials.login and account.password == credentials.password:
            content = {"message": "Login successful"}
            response = JSONResponse(content=content)
            response.set_cookie(key="login", value=credentials.login)
            return response

    raise HTTPException(status_code=400, detail="Invalid login/password supplied")


@app.get("/Accounts/logout", tags=["Accounts"])
async def logout(
        request: Request,
        ##login: str = Cookie(None)
):
    login = request.cookies.get('login')

    if login is not (None or ""):
        content = {"message": "Logout successful"}
        response = JSONResponse(content=content)
        response.set_cookie(key="login", value="")
        return response
    else:
        raise HTTPException(status_code=401, detail="No user is currently logged in")


@app.get("/Accounts", response_model=List[Account], tags=["Accounts"])
async def get_accounts_by_name(
        request: Request,
        first_name: Optional[str] = Query(None, description="The first name to search for."),
        last_name: Optional[str] = Query(None, description="The last name to search for."),
        ##login: str = Cookie(None)  # Извлекаем логин из куки
):
    login = request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=401, detail="No user is currently logged in")

    connect_db()
    results = []
    for account in accounts_db:
        if (first_name and account.firstName.lower() == first_name.lower()) and (
                last_name and account.surName.lower() == last_name.lower()):
            results.append(account)

    if not results:
        raise HTTPException(status_code=404, detail="Accounts not found")

    return results


@app.put("/Accounts", tags=["Accounts"])
async def update_account_name(
        request: Request,
        new_first_name: str = Query(..., description="New first name for the account"),
        new_last_name: str = Query(..., description="New last name for the account"),
        ##login: str = Cookie(None)  # Логин извлекается автоматически из куки
):
    login = request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=401, detail="No user is currently logged in")

    connect_db()
    # Поиск аккаунта по логину
    account_to_update = next((account for account in accounts_db if account.login == login), None)

    if account_to_update is None:
        raise HTTPException(status_code=404, detail="Account not found")

    # Обновление имени и фамилии аккаунта
    account_to_update.firstName = new_first_name
    account_to_update.surName = new_last_name

    return {"message": "Account name updated successfully"}


@app.delete("/Accounts", tags=["Accounts"])
async def delete_account(
        request: Request,
        ##login: str = Cookie(None)
):  # Логин извлекается автоматически из куки
    login = request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=401, detail="No user is currently logged in")

    connect_db()
    # Поиск аккаунта по логину
    account_to_delete = next((account for account in accounts_db if account.login == login), None)

    if account_to_delete is None:
        raise HTTPException(status_code=404, detail="Account not found")

    # Удаляем аккаунт из соответствующей базы данных в зависимости от роли

    if account_to_delete.type_role == "artist":
        artist_db_index = next((index for index, a in enumerate(artists_db) if a.login == login), None)

        # Если художник не найден, возвращаем 404
        if artist_db_index is None:
            raise HTTPException(status_code=404, detail="Artist not found")

        # Удаляем художник из базы данных
        artists_db.pop(artist_db_index)

    if account_to_delete.type_role == "visitor":
        visitor_db_index = next((index for index, a in enumerate(visitors_db) if a.login == login), None)

        # Если посетитель не найден, возвращаем 404
        if visitor_db_index is None:
            raise HTTPException(status_code=404, detail="Visitor not found")

        # Удаляем посетителя из базы данных
        visitors_db.pop(visitor_db_index)

    # Удаляем аккаунт из базы данных
    accounts_db.remove(account_to_delete)

    await logout(request)

    return {"message": "Account deleted successfully"}


###########################################################################################


@app.put("/Visitors", response_model=Visitor, tags=["Visitors"])
async def update_visitor(
        request: Request,
        new_residence: str,
        ##login: str = Cookie(None)  # Извлекаем логин из куки
):
    login = request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    connect_db()
    # Ищем посетителя по ID
    existing_visitor = next((visitor for visitor in visitors_db if visitor.login == login), None)

    if existing_visitor is None:
        raise HTTPException(status_code=404, detail="Denied, you are not visitor")

    # Обновляем место жительства
    existing_visitor.residence = new_residence
    return existing_visitor


@app.get("/Visitors/{visitor_id}", response_model=Visitor, tags=["Visitors"])
async def get_visitor_by_id(
        request: Request,
        visitor_id: int = Path(..., description="ID of Visitor to return"),
        ##login: str = Cookie(None)  # Извлекаем логин из куки
):
    login = request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    connect_db()
    # Ищем посетителя по ID
    visitor = next((visitor for visitor in visitors_db if visitor.id == visitor_id), None)

    if visitor is None:
        raise HTTPException(status_code=404, detail="Visitor not found")

    return visitor


@app.get("/Visitors", response_model=List[Visitor], tags=["Visitors"])
async def get_all_visitors(
        request: Request,
        ##login: str = Cookie(None)  # Извлекаем логин из куки
):
    login = request.cookies.get('login')
    if login is None or login == "":
        raise HTTPException(status_code=403, detail="User not logged in")

    connect_db()

    # Возвращаем всех посетителей
    return visitors_db  # Предполагается, что visitors_db - это список всех посетителей
