from __future__ import annotations

from typing import Any, Callable, Optional, TextIO, Tuple
from typing import Generic, TypeVar
from dataclasses import dataclass, field

import threading
import socket
import select
import sys

from cli import AdminCli, ParsedCommand
from processamento import Process
from protocol import Request, Response

HOST = ''
PORT = 5000

T = TypeVar('T')

def log(s: str) -> None:
    print(s, file=sys.stderr)

@dataclass(eq=False, frozen=True)
class SharedDict:
    lock: threading.Lock = field(init=False, default_factory=threading.Lock)
    process: Process

    @staticmethod
    def from_file(filename: str) -> SharedDict:
        return SharedDict(Process.from_file(filename))

@dataclass()
class Server(Generic[T]):
    sock: socket.socket
    port: int
    shared_mut: T
    all_threads: list[threading.Thread]
    on_start: Callable[[T], None]
    on_stdin: Callable[[T, TextIO, TextIO], bool]
    on_newsock: Callable[[T, Tuple[socket.socket, str]], None]
    on_exit: Callable[[T], None]

    def __init__(self,
            host: str,
            port: int,
            shared_mut: T,
            on_start: Callable[[T], None],
            on_stdin: Callable[[T, TextIO, TextIO], bool],
            on_newsock: Callable[[T, Tuple[socket.socket, str]], None],
            on_exit: Callable[[T], None],
            ) -> None:
        self.sock = \
            socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM | socket.SOCK_NONBLOCK
        )
        self.sock.bind((host, port))
        self.sock.listen(5)
        assert self.sock.getblocking() == False
        # self.sock.setblocking(False)

        self.port = port
        self.shared_mut = shared_mut
        self.all_threads = []
        self.on_start = on_start
        self.on_stdin = on_stdin
        self.on_newsock = on_newsock
        self.on_exit = on_exit

    def __enter__(self) -> Server[T]:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
        self.on_exit(self.shared_mut)

    def close(self) -> None:
        log(f"Closing socket...")
        self.sock.close()
        log(f"Waiting for threads...")
        for t in self.all_threads:
            t.join()
        log(f"Exiting...")

    def accept(self) -> Tuple[socket.socket, str]:
        args: Tuple[socket.socket, str] = self.sock.accept()
        thread: threading.Thread = \
            threading.Thread(
                target=self.on_newsock,
                args=(self.shared_mut, args)
        )
        thread.start()
        self.all_threads.append(thread)
        return args

    def run(self) -> None:
        stop: bool = False
        ins = [sys.stdin, self.sock]

        log(f"Running on port {self.port}...")
        self.on_start(self.shared_mut)
        while not stop:
            read, _write, _exeption = select.select(ins, [], [])
            for inp in read:
                if inp == sys.stdin:
                    stop = self.on_stdin(self.shared_mut, sys.stdin, sys.stdout)
                elif inp == self.sock:
                    _sock_addr: Tuple[socket.socket, str] = \
                        self.accept()
                else:
                    assert False, 'unreachable'

def init(shared_mut: SharedDict) -> None:
    AdminCli.help(sys.stdout)

def run_thread(
        shared_mut: SharedDict,
        sock_addr: Tuple[socket.socket, str]
        ) -> None:
    sock: socket.socket = sock_addr[0]
    addr: str = sock_addr[1][0] + ' : ' + str(sock_addr[1][1])
    log(f"Client connected: {addr} ...")
    while True:
        request: Optional[Request] = Request.read(sock)
        if request is None:
            break
        log(f"Received request from {addr}")
        assert request is not None
        response: Optional[Response] = None
        if isinstance(request.inner, Request.Read):
            read_req: Request.Read = request.inner
            with shared_mut.lock:
                val_list: list[str] = \
                    shared_mut.process.read(read_req.key)
            response = Response(Response.Read(
                key = read_req.key,
                val_list = val_list,
            ))
        elif isinstance(request.inner, Request.Append):
            append_req: Request.Append = request.inner
            with shared_mut.lock:
                existed_before: bool = \
                    shared_mut.process.append(
                        append_req.key,
                        append_req.val,
                )
                response = Response(
                    Response.AppendExists()
                    if existed_before
                    else Response.AppendNotExists()
                )
        else:
            assert False, 'unreachable'
        assert response is not None
        response.write(sock)
        log(f"Response sent to {addr}")
    log(f"Client disconnected: {addr} ...")

def run_user(
        shared_mut: SharedDict,
        input: TextIO,
        output: TextIO,
        ) -> bool:
    parsed: Optional[ParsedCommand] = \
        AdminCli.command(input, sys.stdout)
    if parsed is None:
        # Nothing to do
        pass
    elif parsed.cmd_name == 'append':
        assert len(parsed.args) == 2
        with shared_mut.lock:
            existed_before: bool = shared_mut.process\
                .append(parsed.args[0], parsed.args[1])
        if existed_before:
            print('=> Existed before!',
                file=output)
        else:
            print('=> Just created!',
                file=output)
    elif parsed.cmd_name == 'read':
        assert len(parsed.args) == 1
        with shared_mut.lock:
            val_list = shared_mut.process \
                .read(parsed.args[0])
        print(f"=> Read values (len: {len(val_list)}): {val_list}",
            file=output)
    elif parsed.cmd_name == 'remove':
        assert len(parsed.args) == 1
        with shared_mut.lock:
            val_list = shared_mut.process. \
            remove(parsed.args[0])
        print(f"=> Removed values (len: {len(val_list)}): {val_list}",
            file=output)
    elif parsed.cmd_name == 'load':
        assert len(parsed.args) == 0
        with shared_mut.lock:
            shared_mut.process.load()
        print('=> Loaded ok',
            file=output)
    elif parsed.cmd_name == 'store':
        assert len(parsed.args) == 0
        with shared_mut.lock:
            shared_mut.process.store()
        print('=> Stored ok',
            file=output)
    elif parsed.cmd_name == 'exit':
        return True
    elif parsed.cmd_name == 'help':
        AdminCli.help(output)
    else:
        log(f"cmd: '{parsed.cmd_name}'")
        for i, arg in enumerate(parsed.args):
            log(f"arg {i}: '{arg}'")
        assert False, f"Unhandled command: '{parsed.cmd_name}'"
    return False

def noop(shared_mut: T) -> None:
    return None

def create_server(dict_file: str) -> Server[SharedDict]:
    shared_dict: SharedDict = SharedDict.from_file(dict_file)
    return Server(
        HOST, PORT,
        shared_mut = shared_dict,
        on_start = init,
        on_stdin = run_user,
        on_newsock = run_thread,
        on_exit = noop
    )

def main(dict_file: str) -> int:
    with create_server(dict_file) as server:
        server.run()
    return 0

if __name__ == '__main__':
    dict_file: str = 'start_dict.json'
    retcode: int = main(dict_file)
    sys.exit(retcode)
