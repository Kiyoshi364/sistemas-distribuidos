from dataclasses import dataclass, field

@dataclass(eq=False, frozen=True, slots=True)
class Dicionario:
    dic: dict[str, list[str]] = field(default_factory=dict)

    def append(self, key: str, val: str) -> bool:
        """
        Adiciona `val` na lista da chave `key`.
        Retorna se existia a chave `key` antes de chamar a função.
        Observe que caso já exista `val` na lista de `key`,
        ela estará duplicada.
        **Altera estado interno.**
        """
        in_dict: bool = key in self.dic
        old_val: list[str] = self.dic.get(key, [])
        old_val.append(val)
        self.dic[key] = old_val
        return in_dict

    def read(self, key: str) -> list[str]:
        """
        Retorna os valores de `key`.
        Lista vazia representa que key não está no dicionário.
        """
        val: list[str] = self.dic.get(key, [])
        assert key not in self.dic or len(val) > 0
        return val

    def remove(self, key: str) -> list[str]:
        """
        Remove os valores de `key`.
        Retorna o valor da entrada removida (semelhante a `read`).
        **Altera estado interno.**
        """
        if key in self.dic:
            return self.dic.pop(key)
        else:
            return []

