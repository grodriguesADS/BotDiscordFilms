# BotDiscordFilms

BotDiscordFilms is a Discord bot designed to help users find and share information about films. It can search for movies, provide details, and recommend films based on user preferences.

## Features

- Search for movies by title
- Get detailed information about a movie
- Receive movie recommendations
- Share movie details with other users in the Discord server

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/grodriguesADS/BotDiscordFilms.git
    ```
2. Navigate to the project directory:
    ```bash
    cd BotDiscordFilms
    ```
3. Install the required dependencies:
    ```bash
    npm install
    ```

## Usage

1. Create a `.env` file in the root directory and add your Discord bot token:
    ```
    DISCORD_TOKEN=your_discord_bot_token
    ```
2. Start the bot:
    ```bash
    npm start
    ```

## Commands

- `db!addfilme <nome do filme>`: Add a movie to the list.
- `db!removefilme <nome do filme>`: Remove a movie from the list.
- `db!listafilmes`: Display all movies in the list.
- `db!procurafilme <nome do filme>`: Search for a movie on TMDB.
- `db!geraarquivo`: Generate a list of movies in the list.
- `db!tempofilme <nome do filme>`: Inform the time the movie ends.
- `db!limpafilmes`: Remove all movies from the list.
- `db!sorteafilme`: Pick a random movie to watch.
- `db!removefilmeusuario <@usuário>`: Remove all movies added by the user.
- `db!help`: Show this help message.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please contact [grodriguesADS](mailto:guilherme.ads.2022@gmail.com).
