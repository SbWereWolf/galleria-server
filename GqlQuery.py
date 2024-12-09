from typing import Optional, List

import strawberry

from GqlObjectTypes import AccountType, VisitorType, ArtistType, \
    VoucherType
from models import find_all_accounts, find_visitor, \
    find_all_visitors, find_artist, find_all_artists, find_voucher, \
    find_all_vouchers


@strawberry.type
class GraphQLQuery:
    @strawberry.field
    def accounts(
            self,
            session_id: str,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
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
            style_list: Optional[List[str]] = None,
    ) -> List[ArtistType]:
        return find_all_artists(session_id, style_list)

    @strawberry.field
    def voucher(self, session_id: str, voucher_id: int) -> VoucherType:
        return find_voucher(session_id, voucher_id)

    @strawberry.field
    def vouchers(
            self,
            session_id: str,
            style: Optional[List[str]],
            status: Optional[List[str]],
    ) -> List[VoucherType]:
        return find_all_vouchers(session_id, style, status)
