from __future__ import annotations

from typing import Optional, Union
from dataclasses import dataclass
from enum import IntEnum

import socket

MAGIC: bytes = b'HDD'

class ReqAction(IntEnum):
    READ   = 0x01
    APPEND = 0x02

    @staticmethod
    def all_actions() -> list[ReqAction]:
        return [
            ReqAction.READ,
            ReqAction.APPEND,
        ]

    @staticmethod
    def from_byte(b: bytes) -> ReqAction:
        assert len(b) == 1
        for action in ReqAction.all_actions():
          if b[0] == action.value:
              return action
        assert False, 'unreachable'

    def to_byte(self) -> bytes:
        if self == ReqAction.READ:
            return b'\x01'
        elif self == ReqAction.APPEND:
            return b'\x02'
        else:
            assert False, 'unreachable'

class RespAction(IntEnum):
    READ              = 0x01
    APPEND_NOT_EXISTS = 0x02
    APPEND_EXISTS     = 0x03

    @staticmethod
    def all_actions() -> list[RespAction]:
        return [
            RespAction.READ,
            RespAction.APPEND_NOT_EXISTS,
            RespAction.APPEND_EXISTS,
        ]

    @staticmethod
    def from_byte(b: bytes) -> RespAction:
        assert len(b) == 1
        for action in RespAction.all_actions():
          if b[0] == action.value:
              return action
        assert False, 'unreachable'

    def to_byte(self) -> bytes:
        if self == RespAction.READ:
            return b'\x01'
        elif self == RespAction.APPEND_NOT_EXISTS:
            return b'\x02'
        elif self == RespAction.APPEND_EXISTS:
            return b'\x03'
        else:
            assert False, 'unreachable'

class Common:
    @staticmethod
    def read_magic(sock: socket.socket) -> bool:
        magic_left: int = 3
        while magic_left > 0:
            data: bytes = sock.recv(magic_left)
            if len(data) == 0:
                return False
            for d in data:
                if d == MAGIC[-magic_left]:
                    magic_left -= 1
                else:
                    magic_left = 3
        return True

    @staticmethod
    def write_magic(sock: socket.socket) -> None:
        sock.send(MAGIC)

    @staticmethod
    def read_req_action(sock: socket.socket) -> ReqAction:
        data: bytes = sock.recv(1)
        assert len(data) == 1
        return ReqAction.from_byte(data)

    @staticmethod
    def write_req_action(sock: socket.socket, action: ReqAction) -> None:
        data: bytes = action.to_byte()
        sock.send(data)

    @staticmethod
    def read_resp_action(sock: socket.socket) -> RespAction:
        data: bytes = sock.recv(1)
        assert len(data) == 1
        return RespAction.from_byte(data)

    @staticmethod
    def write_resp_action(sock: socket.socket, action: RespAction) -> None:
        data: bytes = action.to_byte()
        sock.send(data)

    @staticmethod
    def read_zero_number(sock: socket.socket) -> int:
        data: bytes = sock.recv(1)
        assert len(data) == 1
        return int(data.hex(), 16)

    @staticmethod
    def write_zero_number(sock: socket.socket, num: int) -> None:
        assert 0 <= num and num <= 0xFF
        sock.send(num.to_bytes(1, 'big'))

    @staticmethod
    def read_one_number(sock: socket.socket) -> int:
        num: int = Common.read_zero_number(sock)
        return num + 1

    @staticmethod
    def write_one_number(sock: socket.socket, num: int) -> None:
        assert 1 <= num and num <= 0x100
        Common.write_zero_number(sock, num - 1)

    @staticmethod
    def read_str_utf8(sock: socket.socket, str_len: int) -> str:
        assert str_len > 0
        data: bytes = b''
        while len(data) < str_len:
            tmp: bytes = sock.recv(str_len - len(data))
            assert len(tmp) > 0
            data += tmp
        return data.decode('utf-8')

    @staticmethod
    def write_str_utf8(sock: socket.socket, s: str) -> None:
        sock.send(s.encode('utf-8'))

    @staticmethod
    def read_zero_str_utf8(sock: socket.socket) -> str:
        str_len: int = Common.read_zero_number(sock)
        return Common.read_str_utf8(sock, str_len)

    @staticmethod
    def write_zero_str_utf8(sock: socket.socket, s: str) -> None:
        str_len: int = len(s)
        assert str_len <= 0xFF
        Common.write_zero_number(sock, str_len)
        Common.write_str_utf8(sock, s)

    @staticmethod
    def read_one_str_utf8(sock: socket.socket) -> str:
        str_len: int = Common.read_one_number(sock)
        return Common.read_str_utf8(sock, str_len)

    @staticmethod
    def write_one_str_utf8(sock: socket.socket, s: str) -> None:
        str_len: int = len(s)
        assert 0 < str_len and str_len <= 0x100
        Common.write_one_number(sock, str_len)
        Common.write_str_utf8(sock, s)

@dataclass(frozen=True)
class Request:
    inner: Union[Request.Read, Request.Append]

    @staticmethod
    def read(sock: socket.socket) -> Optional[Request]:
        if not Common.read_magic(sock):
            return None
        action: ReqAction = Common.read_req_action(sock)
        key: str = Common.read_one_str_utf8(sock)
        if action == ReqAction.READ:
            return Request(Request.Read(
                key = key
            ))
        elif action == ReqAction.APPEND:
            val: str = Common.read_one_str_utf8(sock)
            return Request(Request.Append(
                key = key,
                val = val,
            ))
        else:
            assert False, 'unreachable'

    def write(self, sock: socket.socket) -> None:
        self.inner.write(sock)

    @dataclass(frozen=True, kw_only=True)
    class Read:
        key: str

        def write(self, sock: socket.socket) -> None:
            Common.write_magic(sock)
            Common.write_req_action(sock, ReqAction.READ)
            Common.write_one_str_utf8(sock, self.key)

    @dataclass(frozen=True, kw_only=True)
    class Append:
        key: str
        val: str

        def write(self, sock: socket.socket) -> None:
            Common.write_magic(sock)
            Common.write_req_action(sock, ReqAction.APPEND)
            Common.write_one_str_utf8(sock, self.key)
            Common.write_one_str_utf8(sock, self.val)

@dataclass(frozen=True)
class Response:
    inner: Union[Response.Read, Response.AppendNotExists, Response.AppendExists]

    @staticmethod
    def read(sock: socket.socket) -> Optional[Response]:
        if not Common.read_magic(sock):
            return None
        action: RespAction = Common.read_resp_action(sock)
        if action == RespAction.READ:
            key: str = Common.read_one_str_utf8(sock)
            val_count: int = Common.read_zero_number(sock)
            val_list: list[str] = []
            for i in range(val_count):
                val_list.append(Common.read_one_str_utf8(sock))
            return Response(Response.Read(
                key = key,
                val_list = val_list,
            ))
        elif action == RespAction.APPEND_NOT_EXISTS:
            return Response(Response.AppendNotExists())
        elif action == RespAction.APPEND_EXISTS:
            return Response(Response.AppendExists())
        else:
            assert False, 'unreachable'

    def write(self, sock: socket.socket) -> None:
        self.inner.write(sock)

    @dataclass(frozen=True, kw_only=True)
    class Read:
        key: str
        val_list: list[str]

        def write(self, sock: socket.socket) -> None:
            Common.write_magic(sock)
            Common.write_resp_action(sock, RespAction.READ)
            Common.write_one_str_utf8(sock, self.key)
            Common.write_zero_number(sock, len(self.val_list))
            for val in self.val_list:
                Common.write_one_str_utf8(sock, val)

    @dataclass(frozen=True, kw_only=True)
    class AppendNotExists:

        def write(self, sock: socket.socket) -> None:
            Common.write_magic(sock)
            Common.write_resp_action(sock, RespAction.APPEND_NOT_EXISTS)

    @dataclass(frozen=True, kw_only=True)
    class AppendExists:

        def write(self, sock: socket.socket) -> None:
            Common.write_magic(sock)
            Common.write_resp_action(sock, RespAction.APPEND_EXISTS)

