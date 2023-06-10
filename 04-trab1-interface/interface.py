from __future__ import annotations

from typing import Callable, Optional, Tuple, TypeAlias
from dataclasses import dataclass

import rpyc # type: ignore

UserId: TypeAlias = int

# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only
@dataclass(frozen=True, kw_only=True, slots=True)
class UserInfo:
    user_id: UserId
    user_name: str

Topic: TypeAlias = str

# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only
@dataclass(frozen=True, kw_only=True, slots=True)
class Content:
    author: UserId
    topic: Topic
    data: str

# Aqui pode ser uma função que recebe apenas um Tuple[Topic, Content]
# ou seja:
# FnNotify: TypeAlias = Callable[[Tuple[Topic, Content]], None]
FnNotify: TypeAlias = Callable[[list[Tuple[Topic, Content]]], None]

class BrokerService(rpyc.Service): # type: ignore

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(self, id: UserId, topicname: str) -> Topic:
        assert False, "TO BE IMPLEMENTED"

    # Handshake

    def exposed_login(self, username: str) -> Optional[UserId]:
        assert False, "TO BE IMPLEMENTED"

    # Query operations

    def exposed_get_user_info(self, id: UserId) -> UserInfo:
        assert False, "TO BE IMPLEMENTED"

    def exposed_list_topics(self) -> list[Topic]:
        assert False, "TO BE IMPLEMENTED"

    # Publisher operations

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> None:
        assert False, "TO BE IMPLEMENTED"

    # Subscriber operations

    def exposed_subscribe_to(self, id: UserId, topic: Topic, callback: FnNotify) -> Optional[FnNotify]:
        assert False, "TO BE IMPLEMENTED"

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> Optional[FnNotify]:
        assert False, "TO BE IMPLEMENTED"

    # Nota: A semântica do subscribe_all não foi definida, opções:
    # 0 - Jogar essa função fora (e unsubscribe_all)
    # 1 - Se um topico for criado depois, deve inscrever o User nele
    # 2 - Se um topico for criado depois, não deve inscrever o User nele
    #
    # a: nos casos (0) e (2) fazem sentido se inscrever no "evento" de "novo tópico"
    def exposed_subscribe_all(self, id: UserId, callback: FnNotify) -> Optional[FnNotify]:
        assert False, "TO BE IMPLEMENTED"

    # Nota: não sei como deve ser o retorno dessa função,
    # talvez: dict[Topic, Optional[FnNotify]]
    def exposed_unsubscribe_all(self, id: UserId) -> FnNotify:
        assert False, "TO BE IMPLEMENTED"
