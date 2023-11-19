# NEAT-GAME

NEAT-GAME is an AI-driven game developed in Python, utilizing the NeuroEvolution of Augmenting Topologies (NEAT) algorithm. This project draws inspiration from "Python Flappy Bird AI Tutorial (with NEAT)" by Tech With Tim on YouTube.

## Overview

The game features a character (the "Boy") who must avoid obstacles (meatballs) falling from the sky. The core of this project is to train an AI using the NEAT algorithm to play the game efficiently. The AI evolves through generations, learning to dodge obstacles better with each iteration.

## Getting Started

### Prerequisites

- Python 3
- Pygame
- NEAT-Python
- pickle (for saving and loading AI genomes)

### Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:Fredd124/Chovem-Almondegas-NEAT-IA.git
   cd Chovem-Almondegas-NEAT-IA
   ```
2. Install the required Python libraries:
   ```bash
   pip install pygame neat-python
   ```
## Project Structure 

  * game.py: The main game script for manual play.
  * NEAT-game.py: The script to run the game with AI using NEAT.
  * config-feedforward.txt: Configuration file for NEAT parameters.
  * best.pickle: Serialized file containing a previous trained NEAT genome.

## Usage

  * To play the game manually, run game.py.
  * To observe the AI play the game, run NEAT-game.py. This will initiate the training process, evolving the AI over generations.
  * To use a pre-trained AI, ensure best.pickle is in the project directory and change the last lines of code present in the NEAT-game.py. The AI will be loaded from the best.pickle file.

## Customization

  * AI configurations can be adjusted in config-feedforward.txt. Parameters like population size, fitness criteria, and network topology can be tweaked here.
  * To understand the configuration settings, refer to the [NEAT documentation](https://neat-python.readthedocs.io/en/latest/)

## How It Works

  The game utilizes Pygame for rendering and handling game mechanics. The NEAT algorithm, implemented through the NEAT-Python library, is used to train an AI to play the game. The AI receives input from the game state and decides on actions to avoid obstacles. With each generation, the AI's performance is evaluated, and the most successful neural network topologies are used to breed the next generation.

