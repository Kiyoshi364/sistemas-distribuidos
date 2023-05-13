from typing import Any, Optional, TextIO
from dataclasses import dataclass, field

import rpyc # type: ignore

import sys

from cli import AdminCli, ParsedCommand

HOST = 'localhost'
PORT = 5000

def log(s: str) -> None:
    print(s, file=sys.stderr)

@dataclass(eq=False, kw_only=True, slots=True)
class ConnMan:
    host: str
    port: int
    conn: rpyc.Connection = field(init=False)

    def __enter__(self) -> rpyc.Connection:
        self.conn = rpyc.connect(self.host, self.port)
        log(f"connected to service: {'conn.root.get_service_name()'}")
        return self.conn

    def __exit__(self, *args: Any) -> None:
        self.conn.close()

def create_conn(
        host: str,
        port: int,
        ) -> ConnMan:
    return ConnMan(host=host, port=port)

def handle_command(
        parsed: ParsedCommand,
        conn: rpyc.Connection,
        output: TextIO,
        ) -> bool:
    if parsed.cmd_name == 'append':
        assert len(parsed.args) == 2
        in_dict_before = \
            conn.root.append(parsed.args[0], parsed.args[1])
        if not in_dict_before:
            print('=> Just created!',
                file=output)
        else:
            print('=> Existed before!',
                file=output)
    elif parsed.cmd_name == 'read':
        assert len(parsed.args) == 1
        read_list = conn.root.read(parsed.args[0])
        print(f"=> Read '{parsed.args[0]}' values (len: {len(read_list)}): {read_list}",
            file=output)
    elif parsed.cmd_name == 'remove':
        assert len(parsed.args) == 1
        rem_list = conn.root.remove(parsed.args[0])
        print(f"=> Remove '{parsed.args[0]}' values (len: {len(rem_list)}): {rem_list}",
            file=output)
    elif parsed.cmd_name == 'load':
        assert len(parsed.args) == 0
        conn.root.load()
        print(f"=> Dictionary reloaded",
            file=output)
    elif parsed.cmd_name == 'store':
        assert len(parsed.args) == 0
        conn.root.store()
        print(f"=> Dictionary stored",
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

def main() -> int:
    infile = sys.stdin
    outfile = sys.stdout
    with create_conn(HOST, PORT) as conn:
        should_stop: bool = False
        AdminCli.help(outfile)
        while not should_stop:
            parsed: Optional[ParsedCommand] = \
                AdminCli.command(infile, outfile)
            if parsed is None:
                # Nothing to do
                pass
            else:
                should_stop = handle_command(parsed, conn, outfile)
    return 0

if __name__ == "__main__":
    sys.exit(main())

