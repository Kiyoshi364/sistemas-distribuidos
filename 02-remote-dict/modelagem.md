---

---
# Atividade 1

## Estilo Arquitetural

* Em camadas

## Componentes

* (0) Persistência
  * Conversa com o disco para carregar e salvar o dicionário
  * Expõe:
    * ```python
        def load(path: str) -> Dicionario
      ```
      Lê o Dicionário do `path`.
    * ```python
        def store(dict: Dicionario, path: str) -> None
      ```
      Salva o Dicionário no `path`.

* (1) Dicionário (acesso R/W)
  * Implementa um dicionário de `str` para `list[str]`
  * Expõe:
    * ```python
        def append(*self, key: str, val: str) -> bool
      ```
      Adiciona `val` na lista da chave `key`.
      Retorna se existia a chave `key` antes de chamar a função.
      Observe que caso já exista `val` na lista de `key`,
      ela estará duplicada.
      **Altera estado interno.**

    * ```python
        def read(self, key: str) -> list[str]
      ```
      Retorna os valores de `key`.
      Lista vazia representa que key não está no dicionário.

    * ```python
        def remove(*self, key: str) -> list[str]
      ```
      Remove os valores de `key`.
      Retorna o valor da entrada removida (semelhante a `read`).
      **Altera estado interno.**

---
* (2) Processamento de Requisições
  * Observa a requisição e decide o que fazer

  * As **Requisições** são ligadas diretamente
  com as funcionalidades de (0) e (1):
    * (r0): relacionado com _(0).load_
    * (r1): relacionado com _(0).store_
    * (r2): relacionado com _(1).append_
    * (r3): relacionado com _(1).read_
    * (r4): relacionado com _(1).remove_

* (3) Interface Humana
  * Entende o que o usuário quer e gera uma Requisição
  * Observe que apenas o **admin** tem acesso as seguintes **Requisições**:
  * Esse componente vai ser dividido em duas partes:

  * (3a) Interface com **admin**
    * Tem acesso a todas as **Requisições**

  * (3b) Interface com **usuário**
    * Tem acesso as seguintes **Requisições**:
      * _(2).(r2)_
      * _(2).(r3)_

---
# Atividade 2

## Item 1.
Componentes _(2)_, _(3b)_ (sem privilégios de **admin**)

## Item 2.
Componentes _(0)_, _(1)_, _(2)_,
_(3a)_ (com privilégios de **admin**)

## Item 3.

### Protocolos

* (p0) Request-Response
  1. **[Client]**: Envia **Requisição** para **[Server]**
  2. **[Server]**: Processa **Requisição**
  3. **[Server]**: Envia **Resposta** para **[Client]**

#### Modelo da **Requisição**:
  * **Magic** (3 `bytes`):
    * 0x48 0x44 0x44 (a string "HDD")
  * **Ação** (1 `byte`): 
    * **Ações** possíveis:
      1. _read_: 0x01
      2. _append_: 0x02
  * **Tamanho de key** (1 `byte`, `one-encoded`)
  * **key** (**Tamanho de key** `bytes`, `utf8-encoded`)
  * Se **Ação** for _append_:
    * **Tamanho de val** (1 `byte`, `one-encoded`)
    * **val** (**Tamanho de val** `bytes`, `utf8-encoded`)

---
#### Modelo da **Resposta**:
  * **Magic** (3 `bytes`):
    * 0x48 0x44 0x44 (a string "HDD")
  * **Resposta à ação da Requisição** (1 `byte`): 
    * **Respostas** possíveis:
      1. _read_: 0x01
      2. _append_:
          * **key** _não existe_: 0x02
          * **key** _existe_: 0x03
  * Se **Ação** for _read_:
    * **Tamanho de key** (1 `byte`, `one-encoded`)
    * **key** (**Tamanho de key** `bytes`, `utf8-encoded`)
    * **Tamanho da lista de valores** (1 `byte`, `zero-encoded`)
    * Repete **Tamanho da lista de valores** vezes:
      * **Tamanho de val** (1 `byte`, `one-encoded`)
      * **val** (**Tamanho de val** `bytes`, `utf8-encoded`)

**Observe** que `zero-encoded` significa que:
* ler um `0` representa `0`
* ler um `1` representa `1`
* ...
* ler um `n` representa `n`

**Observe** que `one-encoded` significa que:
* ler um `0` representa `1`
* ler um `1` representa `2`
* ...
* ler um `n` representa `n+1`
