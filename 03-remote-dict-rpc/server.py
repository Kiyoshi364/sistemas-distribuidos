from typing import Any
from dataclasses import dataclass, field

import rpyc # type: ignore

import threading
import sys

from processamento import Process

PORT = 5000

@dataclass(eq=False, frozen=True, slots=True)
class HDDService(rpyc.Service): # type: ignore
    lock: threading.Lock = field(init=False, default_factory=threading.Lock)
    process: Process

    def on_connect(self, conn: rpyc.Connection) -> None:
        print('Someone connected')

    def on_disconnect(self, conn: rpyc.Connection) -> None:
        print('Someone disconnected')

    def exposed_load(self) -> None:
        with self.lock:
            return self.process.load()

    def exposed_store(self) -> None:
        with self.lock:
            return self.process.store()

    def exposed_append(self, key: str, val: str) -> bool:
        with self.lock:
            return self.process.append(key, val)

    def exposed_read(self, key: str) -> list[str]:
        with self.lock:
            return self.process.read(key)

    def exposed_remove(self, key: str) -> list[str]:
        with self.lock:
            return self.process.remove(key)

def main(dict_file: str) -> int:
    from rpyc.utils.server import ThreadedServer # type: ignore
    srv = ThreadedServer(
        HDDService(Process.from_file(dict_file)),
        port = PORT
    )
    srv.start()
    return 0

if __name__ == "__main__":
    dict_file: str = 'start_dict.json'
    retcode: int = main(dict_file)
    sys.exit(retcode)
