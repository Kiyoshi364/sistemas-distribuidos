from __future__ import annotations

from typing import Callable, Optional, Tuple, TypeAlias
from dataclasses import dataclass, field

import rpyc # type: ignore
# import time

UserId: TypeAlias = int

# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only
@dataclass(frozen=True, kw_only=True, slots=True)
class UserInfo:
    user_id: UserId
    user_name: str

Tag: TypeAlias = str

# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only
@dataclass(frozen=True, kw_only=True, slots=True)
class Content:
    author: UserId
    tag: Tag
    data: str
    # publish_timestamp: time.struct_time

# Aqui pode ser uma função que recebe apenas um Tuple[Tag, Content]
# ou seja:
# FnNotify: TypeAlias = Callable[[Tuple[Tag, Content]], None]
FnNotify: TypeAlias = Callable[[list[Tuple[Tag, Content]]], None]

class BrokerService(rpyc.Service): # type: ignore

    # Não é exposed porque só o "admin" tem acesso
    def create_tag(self, id: UserId, tagname: str) -> Tag:
        pass

    # Handshake

    def exposed_login(self, username: str) -> Optional[UserId]:
        pass

    # Query operations

    def exposed_get_user_info(self, id: UserId) -> UserInfo:
        pass

    def exposed_list_tags(self) -> list[Tag]:
        pass

    # Publisher operations

    def exposed_publish(self, id: UserId, tag: Tag, data: str) -> None:
        pass

    # Subscriber operations

    def exposed_subscribe_to(self, id: UserId, tag: Tag, callback: FnNotify) -> Optional[FnNotify]:
        pass

    def exposed_subscribe_all(self, id: UserId, callback: FnNotify) -> Optional[FnNotify]:
        pass

    def exposed_unsubscribe_to(self, id: UserId, tag: Tag) -> FnNotify:
        pass

    def exposed_unsubscribe_all(self, id: UserId) -> FnNotify:
        pass
