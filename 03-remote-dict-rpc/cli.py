from typing import NamedTuple, Optional, Tuple, TypeAlias, TextIO

import socket

Command: TypeAlias = Tuple[str, list[str]]
ParsedCommand = NamedTuple('ParsedCommand', [
    ('cmd_name', str),
    ('args', list[str]),
])

class AdminCli:
    CMDS: list[Command] = [
        ('append', ['key', 'value']),
        ('read', ['key']),
        ('remove', ['key']),
        ('load', []),
        ('store', []),
        ('exit', []),
        ('help', []),
    ]

    @staticmethod
    def help(file: TextIO) -> None:
        Private.help(AdminCli.CMDS, file)

    @staticmethod
    def command(
            input: TextIO,
            file: TextIO,
            ) -> Optional[ParsedCommand]:
        cmd_i = Private.command(AdminCli.CMDS, input, file)
        if cmd_i is None:
            AdminCli.help(file)
            return None
        else:
            args: list[str] = \
                Private.args(AdminCli.CMDS[cmd_i], input, file)
            return ParsedCommand(AdminCli.CMDS[cmd_i][0], args)

class Private:
    @staticmethod
    def trim_left(s: str) -> str:
        for i, c in enumerate(s):
            if not c.isspace():
                return s[i:]
        return ''

    @staticmethod
    def trim_right(s: str) -> str:
        for i, c in reversed(list(enumerate(s))):
            if not c.isspace():
                return s[:i+1]
        return ''

    @staticmethod
    def trim(s: str) -> str:
        return Private.trim_right(Private.trim_left(s))

    @staticmethod
    def help(cmds: list[Command], file: TextIO) -> None:
        if len(cmds) > 0:
            print(
                'Available commands:',
                file=file,
            )
            for cmd in cmds:
                end: str = ':' if len(cmd[1]) > 0 else ''
                print(
                    f'    {cmd[0]}{end}',
                    file=file, end=''
                )
                for arg in cmd[1]:
                    print(
                        f' <{arg}>',
                        file=file, end=''
                    )
                print(file=file, end='\n')
            print(
                '',
                'Example:',
                f'    {cmds[0][0]}',
                file=file, sep='\n'
            )
            for arg in cmds[0][1]:
                print(
                    f'    {cmds[0][0]}: {arg}> my {arg}',
                    file=file
                )
            print(file=file)
        else:
            print(
                'No commands',
                file=file
            )

    @staticmethod
    def command(
                cmds: list[Command],
                input: TextIO,
                file: TextIO,
                ) -> Optional[int]:
        cmd_str: str = input.readline()
        cmd_str_trimed: str = Private.trim(cmd_str)
        for i, cmd in enumerate(cmds):
            if cmd_str_trimed == cmd[0]:
                return i
        else:
            print(
                f"Command not understood: '{cmd_str_trimed}'",
                file=file
            )
            return None

    @staticmethod
    def args(full_cmd: Command, input: TextIO, file: TextIO) -> list[str]:
        cmd: str = full_cmd[0]
        cmd_args: list[str] = full_cmd[1]
        ret_list: list[str] = []
        for cmd_arg in cmd_args:
            loop: bool = True
            while loop:
                print(f"{cmd}: {cmd_arg}> ", file=file, end='')
                file.flush()
                arg: str = input.readline()
                arg_trimed: str = Private.trim(arg)
                if len(arg_trimed) > 0:
                    ret_list.append(arg_trimed)
                    loop = False
        return ret_list
