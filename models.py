import logging
from datetime import datetime, timedelta

import jwt

rootLogger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
fileHandler = logging.FileHandler("log.log")
rootLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
rootLogger.addHandler(consoleHandler)


def connect_db():
    connection = None
    """
    try:
        connection = psycopg.connect(user="postgres",
                                    password="root",
                                    host="127.0.0.1",
                                    port="5433",
                                    database="bob")
        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        rootLogger.info("Connection established")
    except (Exception, psycopg.Error) as error :
        print("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if connection:
                cursor.close()
                connection.close()
                ##print("PostgreSQL connection is closed")
                rootLogger.info("PostgreSQL connection is closed")
    """


from fastapi import HTTPException


def get_status():
    return {"status": "healthy"}


from pydantic import BaseModel, Field
from typing import List, Optional, Literal, get_args


class Session(BaseModel):
    login: str = Field(..., example='10')
    session_id: str = Field(..., example='f376407b-2b01-47b2-9e29-892cf7ea1606')


sessions_db = []


class Credentials(BaseModel):
    login: str = Field(..., example='login')
    password: str = Field(..., example='password')


def create_session(credentials: Credentials):
    session_id = ""
    for account in accounts_db:
        if (account.login == credentials.login
                and account.password == credentials.password):
            account_id = find_account_id(account)
            session_id = create_session_token(
                data=
                {
                    "sub": credentials.login,
                    "role": account.type_role,
                    "id": account_id,
                })

            session = Session(
                session_id=session_id,
                login=credentials.login
            )
            sessions_db.append(session)
            break
    if session_id == "":
        raise HTTPException(
            status_code=400,
            detail="Invalid login/password supplied"
        )
    return session_id


# Конфигурация JWT
SECRET_KEY = \
    "a493003e3c0ef4ee0f6ce2dc2363eed49130b7ab54a77c8c12bd5016c9c2e540"
ALGORITHM = "HS256"


def create_session_token(
        data: dict,
        expires_delta: timedelta = timedelta(hours=1)
):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt


def find_account_id(account):
    account_id = ""

    hydrate_account(account)
    if account is not None:
        account_id = account.id

    return account_id


def find_login(session_id: str) -> str:
    rootLogger.debug(f"session_id = `{session_id}` ", )
    session = next((session for session in sessions_db if session.session_id == session_id), None)
    if session is None:
        rootLogger.debug(f"Session not found ", )
        raise HTTPException(status_code=403, detail="User not logged in")
    login = ''
    if session is not None:
        rootLogger.debug(f"Session found login:`{session.login}`, session id:`{session.session_id}`", )
        login = session.login
    return login


def my_login_and_role(token: str):
    account = find_account_by_token(token)
    return {
        "username": account.login,
        "role": account.type_role
    }


def decode_token(token) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    login: str = payload.get("sub")

    if login is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return login


def remove_session(session_id: str = ''):
    rootLogger.debug(f"session_id = `{session_id}` ", )
    session = next((session for session in sessions_db if session.session_id == session_id), None)
    if session is None:
        rootLogger.debug("Session not found ")
        raise HTTPException(status_code=401, detail="No user is currently logged in")
    if session is not None:
        rootLogger.debug(f"Session found login:`{session.login}`, session id:`{session.session_id}`", )
        sessions_db.remove(session)
    return "Ok"


class Account(BaseModel):
    id: int = Field(..., example=10)
    login: str = Field(..., example='10')
    password: str = Field(..., example='theAccounts')
    surName: str = Field(..., example='Green')
    firstName: str = Field(..., example='John')
    patronymic: Optional[str] = Field(None, example='James')
    email: str = Field(..., example='john@email.com')
    type_role: str = Field(..., example='artist')
    phone: str = Field(..., example='12345')
    sex: str = Field(..., example='m')
    date_of_birth: str = Field(..., example='2000-01-01')  # формат даты
    residence: str = Field(..., example='Yaroslavl, st/ Syrkova')


accounts_db = [
    Account(login='artist1', password='password123', surName='Smith',
            firstName='Alice', patronymic='Marie',
            email='alice@email.com', type_role='artist',
            phone='1234567890', sex='f', date_of_birth='1995-05-15',
            residence='', id=0),
    Account(login='artist2', password='password456',
            surName='Johnson', firstName='Bob', patronymic='Marie',
            email='bob@email.com', type_role='artist',
            phone='0987654321', sex='m', date_of_birth='1990-10-10',
            residence='', id=0),
    Account(login='artist3', password='password123', surName='Dean',
            firstName='Amelia', patronymic='Marie',
            email='amelia@email.com', type_role='artist',
            phone='1234567890', sex='f', date_of_birth='1995-05-15',
            residence='', id=0),
    Account(login='visitor1', password='password456', surName='Black',
            firstName='Adam', patronymic='Marie',
            email='adam@email.com', type_role='visitor',
            phone='0987654321', sex='m', date_of_birth='1990-10-10',
            residence='', id=0),
    Account(login='visitor2', password='password123',
            surName='Fisher', firstName='Lily', patronymic='Marie',
            email='lily@email.com', type_role='visitor',
            phone='1234567890', sex='f', date_of_birth='1995-05-15',
            residence='', id=0),
    Account(login='visitor3', password='password456', surName='Gate',
            firstName='Artur', patronymic='Marie',
            email='artur@email.com', type_role='visitor',
            phone='0987654321', sex='m', date_of_birth='1990-10-10',
            residence='', id=0),
]


def create_account(account: Account):
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
    if new_account.surName is None:
        new_account.surName = ''
    if new_account.firstName is None:
        new_account.firstName = ''
    if new_account.patronymic is None:
        new_account.patronymic = ''
    if new_account.email is None:
        new_account.email = ''
    if new_account.type_role is None:
        new_account.type_role = ''
    if new_account.phone is None:
        new_account.phone = ''
    if new_account.sex is None:
        new_account.sex = ''
    if new_account.date_of_birth is None:
        new_account.date_of_birth = ''
    """
    connection=None
    try:        
        connection = psycopg2.connect(user="postgres",
                                    password="root",
                                    host="127.0.0.1",
                                    port="5433",
                                    database="api")
        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        rootLogger.debug("Connection established")
        cursor.execute(
            'INSERT INTO api.account(login,password,sur_name,first_name,patronymic,email,type_role,phone,sex,date_of_birth)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (
                new_account.login, 
                new_account.password, 
                new_account.surName, 
                new_account.firstName, 
                new_account.patronymic, 
                new_account.email, 
                new_account.type_role, 
                new_account.phone,
                new_account.sex,
                new_account.date_of_birth
            )
        )
        connection.commit()        
    except (Exception, psycopg2.Error) as error :
        print("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                rootLogger.debug("PostgreSQL connection is closed")
    """
    if account.type_role == "artist":
        new_artist = Artist(
            id=max((voucher.id for voucher in artists_db), default=0) + 1,
            login=account.login,
            style="realism"
        )
        artists_db.append(new_artist)
    if account.type_role == "visitor":
        new_visitor = Visitor(
            id=max((voucher.id for voucher in visitors_db), default=0) + 1,
            login=account.login,
            residence="None"
        )
        visitors_db.append(new_visitor)
    # Добавляем новую учётную запись в базу данных
    accounts_db.append(new_account)
    return new_account


def find_account_by_token(token) -> Account:
    login = decode_token(token)
    account = find_account_by_login(login)
    if account is None:
        raise HTTPException(
            status_code=404,
            detail=f"Account with login {login} is not found"
        )
    return account


def find_account_by_login(login) -> Account | None:
    account = next(
        (
            account for account in accounts_db
            if account.login == login)
        , None
    )
    return account


def find_all_accounts(
        session_id: str,
        first_name: Optional[str],
        last_name: Optional[str]
):
    find_login(session_id)
    results = []
    if (first_name is None or first_name == '') and (last_name is None or last_name == ''):
        results = accounts_db
    if first_name is not None or last_name is not None:
        for account in accounts_db:
            if (
                    (first_name
                     and (last_name is None or last_name == '')
                     and account.firstName.lower() == first_name.lower()
                    ) or (
                    last_name
                    and (first_name is None or first_name == '')
                    and account.surName.lower() == last_name.lower()
            )
                    or (
                    first_name and first_name != ''
                    and last_name and last_name != ''
                    and account.firstName.lower() == first_name.lower()
                    and account.surName.lower() == last_name.lower()
            )
            ):
                results.append(account)
        if not results:
            raise HTTPException(status_code=404, detail="Accounts not found")
    return results


def write_account(
        session_id: str,
        new_first_name: str,
        new_last_name: str
):
    connect_db()
    login = find_login(session_id)
    # Поиск аккаунта по логину
    account_to_update = next((account for account in accounts_db if account.login == login), None)
    if account_to_update is None:
        raise HTTPException(status_code=404, detail="Account not found")
    # Обновление имени и фамилии аккаунта
    account_to_update.firstName = new_first_name
    account_to_update.surName = new_last_name
    return "Ok"


def remove_account(session_id):
    connect_db()
    login = find_login(session_id)
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
    remove_session(session_id)
    return "Ok"


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


def find_all_styles():
    return get_args(AllowedStyles)


class Artist(BaseModel):
    login: str = Field(..., example='10')
    id: int = Field(..., example=10)
    style: str = Field(..., example='realism')


# Пример базы данных
artists_db = [
    Artist(login='artist1', id=1, style='realism'),
    Artist(login='artist2', id=2, style='impressionism'),
    Artist(login='artist3', id=3, style='modern'),
]


def find_artist_by_account(account: Account | None) -> Artist | None:
    existing_artist = None
    if account is not None and account.type_role == "artist":
        existing_artist = next(
            (
                artist for artist in artists_db
                if artist.login == account.login
            ),
            None
        )
        if existing_artist is None:
            raise HTTPException(
                status_code=404,
                detail=f"{account.login} is artist,"
                       + " but not found in artists db"
            )

    return existing_artist


def find_all_artists(
        session_id: str,
        style_list: Optional[List[str]]
):
    find_login(session_id)
    existing_styles = list()
    if style_list is not None:
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


def find_artist(
        session_id: str,
        artist_id: int
):
    find_login(session_id)
    artist = next((artist for artist in artists_db if artist.id == artist_id), None)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artists not found")
    return artist


def find_artist_style(
        session_id: str,
        login: str
):
    account = find_account_by_token(session_id)
    if account.login != login:
        raise HTTPException(status_code=403, detail="Not authorized")

    artist = find_artist_by_account(account)
    if artist is None:
        raise HTTPException(
            status_code=404,
            detail=f"{account.login} is not artist"
        )

    return [artist.style]


def write_artist(session_id: str, new_style: str):
    connect_db()
    login = find_login(session_id)
    # Ищем артиста по login
    existing_artist = next((artist for artist in artists_db if artist.login == login), None)
    if existing_artist is None:
        raise HTTPException(status_code=404, detail="Denied, you are not artist")
    # Обновляем место жительства
    existing_artist.style = new_style
    return existing_artist


class Visitor(BaseModel):
    login: str = Field(..., example='10')
    id: int = Field(..., example=10)
    residence: str = Field(..., example='Yaroslavl, st/ Syrkova')


visitors_db = [
    Visitor(login='visitor1', id=4, residence='Moscow, Red Square'),
    Visitor(login='visitor2', id=5,
            residence='Saint Petersburg, Nevsky Prospect'),
    Visitor(login='visitor3', id=6,
            residence='Yaroslavl, st/ Syrkova'),
]


def find_visitor_by_account(account: Account | None) -> Visitor | None:
    existing_visitor = None
    if account is not None and account.type_role == "visitor":
        existing_visitor = next(
            (
                visitor for visitor in visitors_db
                if visitor.login == account.login
            ),
            None
        )
        if existing_visitor is None:
            raise HTTPException(
                status_code=404,
                detail=f"{account.login} is visitor,"
                       + " but not found in visitors db"
            )

    return existing_visitor


def find_account(login: str) -> Account | None:
    account = find_account_by_login(login)
    hydrate_account(account)

    return account


def hydrate_account(account):
    visitor = find_visitor_by_account(account)
    if visitor is not None:
        account.id = visitor.id
        account.residence = visitor.residence
    artist = find_artist_by_account(account)
    if artist is not None:
        account.id = artist.id

    return account


def my_account(token: str) -> Account:
    account = find_account_by_token(token)
    hydrate_account(account)

    return account


def find_visitor(
        session_id: str,
        visitor_id: int
):
    find_login(session_id)
    # Ищем посетителя по ID
    visitor = next((visitor for visitor in visitors_db if visitor.id == visitor_id), None)
    if visitor is None:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor


def find_all_visitors(session_id: str):
    find_login(session_id)
    visitors = visitors_db
    return visitors


def write_visitor(
        session_id: str,
        new_residence: str
):
    connect_db()
    login = find_login(session_id)
    # Ищем посетителя по ID
    existing_visitor = next((visitor for visitor in visitors_db if visitor.login == login), None)
    if existing_visitor is None:
        raise HTTPException(status_code=404, detail="Denied, you are not visitor")
    # Обновляем место жительства
    existing_visitor.residence = new_residence
    return existing_visitor


class Voucher(BaseModel):
    id: int = Field(..., example=10)
    customer: str = Field(..., example="198login")
    executor: str = Field(..., example="198login")
    amount_pictures: int = Field(..., example=3)
    price: int = Field(..., example=100)
    description: str = Field(..., example="3 pictures for 100$")
    status: str = Field(..., example='placed')
    style: str = Field(..., example='realism')


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


def find_all_vouchers(
        session_id: str,
        style: Optional[List[str]],
        status: Optional[List[str]]
):
    find_login(session_id)
    if not vouchers_db:
        raise HTTPException(status_code=404, detail="Vouchers not exists, please add someone")
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


def find_voucher(
        session_id: str,
        voucher_id: int
):
    find_login(session_id)
    voucher = next((v for v in vouchers_db if v.id == voucher_id), None)
    if voucher is None:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return voucher


def create_voucher(
        session_id: str,
        voucher: Voucher
):
    connect_db()
    login = find_login(session_id)
    existing_visitor = next((visitor for visitor in visitors_db if visitor.login == login), None)
    if existing_visitor is None:
        raise HTTPException(status_code=404, detail="Visitor not found")
    # Получаем максимальный ID для нового ваучера
    max_id = max((v.id for v in vouchers_db), default=0)
    # Создаем новый предзаказ
    new_voucher = Voucher(
        id=max_id + 1,
        customer=login,
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


def write_voucher(
        session_id: str,
        voucher_id: int,
        new_status: str
):
    connect_db()
    login = find_login(session_id)
    # Ищем художника по login
    existing_artist = next((artist for artist in artists_db if artist.login == login), None)
    if existing_artist is None:
        raise HTTPException(status_code=404, detail="Denied, you are not artist")
    # Ищем ваучер
    existing_voucher = next((v for v in vouchers_db if v.id == voucher_id), None)
    if existing_voucher is None:
        raise HTTPException(status_code=404, detail="Voucher not found")
    if existing_voucher.status != 'placed' and existing_voucher.executor != login:
        raise HTTPException(status_code=403, detail="Access denied: You do not own this voucher record")
    if existing_voucher.status == 'placed' and existing_voucher.executor == "":
        existing_voucher.executor = login
    existing_voucher.status = new_status  # Обновляем только статус
    return existing_voucher


def remove_voucher(
        session_id: str,
        voucher_id: int
):
    connect_db()
    login = find_login(session_id)
    # Ищем посетителя по ID
    existing_visitor = next((visitor for visitor in visitors_db if visitor.login == login), None)
    if existing_visitor is None:
        raise HTTPException(status_code=404, detail="Denied, you are not visitor")
    # Проверяем, что логин пользователя совпадает с владельцем записи
    if existing_visitor.login != login:
        raise HTTPException(status_code=403, detail="Access denied: You do not own this voucher")
    # Находим индекс ваучера с указанным идентификатором
    voucher_index = next((index for index, voucher in enumerate(vouchers_db) if voucher.id == voucher_id), None)
    # Если ваучер не найден, возвращаем 404
    if voucher_index is None:
        raise HTTPException(status_code=404, detail="Voucher not found")
    # Удаляем ваучер из базы данных
    vouchers_db.pop(voucher_index)
    return "Ok"
