import strawberry

from models import Account, Visitor, Artist, Voucher, Credentials


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
