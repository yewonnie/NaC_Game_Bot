# NaC Game Bot 🎮

Welcome to the **NaC Game Bot** repository! This project is a simple yet engaging implementation of the classic game Tic-Tac-Toe (Крестики-нолики) using the Aiogram framework for Telegram bots. Dive into the world of game development with Python and explore the functionality of a bot that can play against users using the Minimax algorithm.

![Tic Tac Toe](https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Tic-tac-toe.svg/1200px-Tic-tac-toe.svg.png)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Game Rules](#game-rules)
- [Minimax Algorithm](#minimax-algorithm)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)
- [Releases](#releases)

## Features

- Play Tic-Tac-Toe against the bot.
- Uses the Minimax algorithm for optimal play.
- Simple setup and easy to use.
- Built with Python and Aiogram for seamless integration with Telegram.

## Installation

To get started with the NaC Game Bot, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yewonnie/NaC_Game_Bot.git
   ```

2. Navigate to the project directory:
   ```bash
   cd NaC_Game_Bot
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your Telegram bot token. You can obtain a token by talking to [BotFather](https://t.me/botfather) on Telegram.

5. Create a `.env` file in the project root and add your token:
   ```
   TELEGRAM_TOKEN=your_bot_token_here
   ```

## Usage

To run the bot, execute the following command in your terminal:

```bash
python main.py
```

Now, open Telegram, search for your bot, and start playing Tic-Tac-Toe!

## Game Rules

The rules of Tic-Tac-Toe are simple:

1. The game is played on a 3x3 grid.
2. Players take turns placing their marks (X or O) in empty squares.
3. The first player to get three of their marks in a row (horizontally, vertically, or diagonally) wins.
4. If all squares are filled and no player has three in a row, the game ends in a draw.

## Minimax Algorithm

The Minimax algorithm is a decision-making algorithm used in game theory. It provides an optimal move for the player assuming that the opponent also plays optimally. The algorithm evaluates all possible moves and chooses the one that maximizes the player's chances of winning while minimizing the opponent's chances.

### How It Works

1. **Tree Structure**: The algorithm builds a tree of possible game states.
2. **Recursion**: It recursively evaluates each state to determine the best possible outcome.
3. **Backtracking**: It backtracks to find the optimal move based on the evaluations of future states.

This algorithm ensures that the bot plays optimally, making it a challenging opponent.

## Technologies Used

- **Python**: The programming language used for this project.
- **Aiogram**: A modern and easy-to-use framework for building Telegram bots.
- **SQLite3**: A lightweight database for storing game data.
- **Git**: For version control and collaboration.

## Contributing

Contributions are welcome! If you would like to contribute to the NaC Game Bot, please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add your feature description"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeature
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Releases

You can find the latest releases of the NaC Game Bot [here](https://github.com/yewonnie/NaC_Game_Bot/releases). Download and execute the files to get the latest features and improvements.

Feel free to explore the "Releases" section for updates and new versions.

![Download](https://img.shields.io/badge/Download%20Latest%20Release-Click%20Here-brightgreen)

## Contact

For any questions or feedback, feel free to reach out. You can open an issue in the repository or contact me directly through my Telegram.

---

Enjoy playing Tic-Tac-Toe with the NaC Game Bot! Have fun and may the best player win!