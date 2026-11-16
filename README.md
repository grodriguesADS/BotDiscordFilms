# BotDiscordFilms

Bot em Python para gerenciar uma lista de filmes em servidores do Discord. O bot usa SQLAlchemy para registrar a lista e consulta o TMDB para buscar informações sobre filmes.

## Como executar

1. Clone o repositório e instale as dependências:

   ```bash
   git clone https://github.com/grodriguesADS/BotDiscordFilms.git
   cd BotDiscordFilms
   python -m pip install -r requirements.txt
   ```

2. Configure as variáveis de ambiente `DISCORD_TOKEN` e `TMDB_API_KEY`. Crie o arquivo local `config/config.py` com o conteúdo abaixo:

   ```python
   import os

   DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
   TMDB_API_KEY = os.environ["TMDB_API_KEY"]
   BOT_PREFIX = "db!"
   ```

   No Discord Developer Portal, habilite **Message Content Intent** para o bot ler comandos com prefixo. Mantenha as credenciais nas variáveis de ambiente.

3. Na raiz do projeto, inicie o bot com `python main.py`.

## Comandos

Os exemplos abaixo usam o prefixo `db!`:

- `db!addfilme <nome>` adiciona um filme.
- `db!listafilmes` exibe a lista de filmes.
- `db!removefilme <nome>` remove um filme.
- `db!procurafilme <título>` busca um filme no TMDB.
- `db!sorteafilme` sorteia um filme da lista.
- `db!help` mostra os comandos disponíveis.

## Contato

[Guilherme Rodrigues](mailto:guilherme.ads.2022@gmail.com)

