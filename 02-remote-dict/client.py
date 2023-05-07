from typing import Any, TextIO, Optional
from dataclasses import dataclass, field

import socket
import sys

from cli import UserCli, ParsedCommand
from protocol import Request, Response

HOST = 'localhost'
PORT = 5000

def log(s: str) -> None:
    print(s, file=sys.stderr)

@dataclass(eq=False, kw_only=True, slots=True)
class SockMan:
    host: str
    port: int
    sock: socket.socket = field(init=False)

    def __enter__(self) -> socket.socket:
        self.sock: socket.socket = \
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        return self.sock

    def __exit__(self, *args: Any) -> None:
        self.sock.close()

def create_sock(
        host: str,
        port: int,
        ) -> SockMan:
    return SockMan(host=host, port=port)

def handle_command(
        parsed: ParsedCommand,
        sock: socket.socket,
        output: TextIO,
        ) -> bool:
    if parsed.cmd_name == 'append':
        assert len(parsed.args) == 2
        request = Request(Request.Append(
            key = parsed.args[0],
            val = parsed.args[1]
        ))
        request.write(sock)
        log(f"Request sent")
        response = Response.read(sock)
        log(f"Response received")
        if response is None:
            return True
        assert not isinstance(response.inner, Response.Read)
        if isinstance(response.inner, Response.AppendNotExists):
            print('=> Just created!',
                file=output)
        elif isinstance(response.inner, Response.AppendExists):
            print('=> Existed before!',
                file=output)
        else:
            assert False, f"Unhandled Response: '{response}'"
    elif parsed.cmd_name == 'read':
        assert len(parsed.args) == 1
        request = Request(Request.Read(
            key = parsed.args[0]
        ))
        request.write(sock)
        log(f"Request sent")
        response = Response.read(sock)
        log(f"Response received")
        if response is None:
            return True
        assert isinstance(response.inner, Response.Read)
        print(f"=> Read '{response.inner.key}' values (len: {len(response.inner.val_list)}): {response.inner.val_list}",
            file=output)
    elif parsed.cmd_name == 'exit':
        return True
    elif parsed.cmd_name == 'help':
        UserCli.help(output)
    else:
        log(f"cmd: '{parsed.cmd_name}'")
        for i, arg in enumerate(parsed.args):
            log(f"arg {i}: '{arg}'")
        assert False, f"Unhandled command: '{parsed.cmd_name}'"
    return False

def main() -> int:
    infile = sys.stdin
    outfile = sys.stdout
    with create_sock(HOST, PORT) as sock:
        should_stop: bool = False
        UserCli.help(outfile)
        while not should_stop:
            parsed: Optional[ParsedCommand] = \
                UserCli.command(infile, outfile)
            if parsed is None:
                # Nothing to do
                pass
            else:
                should_stop = handle_command(parsed, sock, outfile)
    return 0

if __name__ == '__main__':
    retcode: int = main()
    sys.exit(retcode)
