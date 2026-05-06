# tcc-co2

Guia rapido para iniciar o projeto no Windows usando Command Prompt (CMD).

## Requisitos

- Python 3.11 instalado
- pip disponivel

## 1) Abrir a pasta do projeto

No CMD:

```bat
cd c:\Development\tcc-co2
```

## 2) Confirmar Python 3.11

```bat
py -3.11 --version
```

Se esse comando falhar, instale o Python 3.11 e marque a opcao para adicionar ao PATH.

## 3) Criar ambiente virtual .env

```bat
py -3.11 -m venv .env
```

## 4) Ativar o ambiente virtual no CMD

```bat
.env\Scripts\activate.bat
```

Quando ativo, o terminal geralmente mostra o prefixo (.env).

## 5) Atualizar pip e instalar dependencias

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 6) Rodar o script gerador de frames

```bat
python analise_df_principal.py
```

## 7) Rodar o script principal

```bat
python analise_df_principal.py
```

## 8) Sair do ambiente virtual

```bat
deactivate
```

## Observacao para VS Code

Se o VS Code selecionar outro interpretador automaticamente, escolha manualmente o Python dentro da pasta .env para garantir que os pacotes instalados sejam reconhecidos.
