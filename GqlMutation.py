from typing import Optional

import strawberry

from GqlObjectTypes import AccountType, VisitorType, VoucherType
from models import Account, create_account, write_account, \
    remove_account, write_visitor, write_artist, Voucher, \
    create_voucher, write_voucher, remove_voucher, Credentials, \
    create_session, remove_session


@strawberry.input
class AccountInput:
    login: str
    password: str
    surName: str
    firstName: str
    patronymic: Optional[str]
    email: str
    type_role: str
    phone: str
    sex: str
    date_of_birth: str


@strawberry.input
class VoucherInput:
    amount_pictures: int
    price: int
    description: str
    style: str


@strawberry.input
class CredentialsInput:
    login: str
    password: str


@strawberry.type
class GraphQLMutation:
    @strawberry.mutation
    def add_account(
            self,
            account: AccountInput,
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
            voucher: VoucherInput,
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
            input: CredentialsInput,
    ) -> str:
        credentials = Credentials(
            login=input.login,
            password=input.password
        )
        return create_session(credentials)

    @strawberry.mutation
    def log_out(
            self,
            session_id: Optional[str] = None,
    ) -> str:
        return remove_session(session_id)
