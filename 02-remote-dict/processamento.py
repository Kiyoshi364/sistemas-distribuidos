from __future__ import annotations

from dataclasses import dataclass, fields

from persistencia import Persistencia
from dicionario import Dicionario

@dataclass(eq=False, kw_only=True, slots=True)
class Process:
    dic: Dicionario
    filename: str

    @staticmethod
    def from_file(filename: str) -> Process:
        dic = Dicionario(Persistencia.load(filename))
        return Process(
            dic = dic,
            filename = filename
        )

    def load(self) -> None:
        self.dic = Dicionario(
            Persistencia.load(self.filename)
        )

    def store(self) -> None:
        Persistencia.store(self.filename, self.dic.dic)

    def append(self, key: str, val: str) -> bool:
        return self.dic.append(key, val)

    def read(self, key: str) -> list[str]:
        return self.dic.read(key)

    def remove(self, key: str) -> list[str]:
        return self.dic.remove(key)
