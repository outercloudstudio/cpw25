import asyncio
import random
from typing import Literal, TypedDict
from player import GameController, Player

class PlayerStats(TypedDict):
  won: int
  tied: int
  lost: int
  played: int

class RankingStats(PlayerStats):
  username: str
  points: int

def generate_queue(players: dict[str, Player]) -> set[GameController]:
  """
  Generates a queue of all possible games (unordered pairings) between the given players.

  Arguments:
    players: a dictionary mapping player usernames (strings) to unique Player objects

  Returns:
    a set of GameControllers representing all possible games
  """
  usernames = list(players.keys())
  queue = set()
  for player_name in usernames:
    opponents = usernames.copy()
    opponents.remove(player_name)
    for opponent in opponents:
      queue.add(GameController(players[player_name], players[opponent]))
  return queue

def rank_sort(statistics: dict[str, PlayerStats]) -> list[RankingStats]:
  """
  Calculates the score of players in a tournament and ranks them as follows:
    points (3 for a win, 1 for a tie),
    number of wins,
    number of ties,
    random tiebreaker

  Arguments:
    statistics: dict[str, PlayerStats] - key: username, value: PlayerStats object

  Returns:
    an ordered list of RankingStats objects representing the ranking order of players
  """
  rankings: list[RankingStats] = [ { "username": name, "points": 0, **stats } for name, stats in statistics.items() ]
  for player in rankings:
    player["points"] = player["won"] * 3 + player["tied"]
  rankings.sort(key=lambda player: (player["points"], player["won"], player["tied"], random.random()), reverse=True)
  return rankings

class Tournament:
  """
  Representation:
    players: dict[str, Player] - key: username, value: Player object
    available_players: set[Player] - set of Player objects that are not currently in a game
    statistics: dict[str, PlayerStats] - key: username, value: PlayerStats object
    length: int - number of games that will be played
    game_queue: set[GameController] - set of GameController objects representing all games still needing to be played
    completed_games: set[GameController] - set of GameController objects representing all games that have been played
    cancelled: bool - whether the tournament has been cancelled

  Functions:
    constructor: creates a new complete round-robin tournament with the given players
    start(): starts the tournament, running all games and updating rankings
    start_game(): starts a single game in the tournament
    update_statistics(): updates player statistics based on the results of a given game
    compute_status(): returns the current status of the tournament
    cancel(): cancels the tournament
    print_rankings(): prints out a ranking of players in a formatted fashion
  """

  def __init__(self, players: dict[str, Player]) -> None:
    # Check that the input is valid
    if players is None or not isinstance(players, dict) or len(players) < 2:
      print("Error: cannot create tournament with not enough players.")
      self.players: dict[str, Player] = dict()
      self.available_players: set[Player] = set()
      self.statistics: dict[str, PlayerStats] = dict()
      self.game_queue: set[GameController] = set()
      self.length: int = len(self.game_queue)
      self.completed_games: set[GameController] = set()
      self.cancelled: bool = True
      return
    # Create the tournament
    print("Notice: Creating tournament...")
    self.players: dict[str, Player] = { username: player for username, player in players.items() }
    self.available_players: set[Player] = set(self.players.values())
    self.statistics: dict[str, PlayerStats] = { username: { "won": 0, "tied": 0, "lost": 0, "played": 0} for username in players }
    self.game_queue: set[GameController] = generate_queue(players)
    self.length: int = len(self.game_queue)
    self.completed_games: set[GameController] = set()
    self.cancelled: bool = False
    print("Notice: Tournament created.")

  async def start(self):
    """
    Runs a complete round-robin tournament.

    Prints out the ranking of players in a formatted fashion.

    If not enough players are present, prints that to the console.
    """
    # Ensure that there are enough players to start the tournament
    if len(self.players) < 2:
      print(f"Error: cannot start tournament with {len(self.players)} players.")
      return
    # Start the tournament
    print("Notice: Starting tournament...")
    self.print_rankings()
    # Run all games
    while self.compute_status() == "running":
      if len(self.available_players) > 0:
        # Start any games that are ready to be played
        for game in self.game_queue.copy():
          if game.player1 in self.available_players and game.player2 in self.available_players:
            # Set this game to run concurrently
            print(f"Notice: Starting game between {game.player1.username} and {game.player2.username}.")
            self.game_queue.remove(game)
            self.available_players.remove(game.player1)
            self.available_players.remove(game.player2)
            asyncio.create_task(self.start_game(game))
          await asyncio.sleep(0)
      # Yield control to the event loop for a bit
      await asyncio.sleep(0)
    # Print the final rankings
    self.print_rankings()
    return
  
  async def start_game(self, game: GameController) -> None:
    """
    Plays a single game in the tournament. Assumes that both players are not currently in another game.
    Updates the rankings based on the results of the given completed GameController.

    Arguments:
      game: GameController - the game to begin
    """
    await game.play_game()
    self.update_statistics(game)
    self.completed_games.add(game)
    self.available_players.add(game.player1)
    self.available_players.add(game.player2)
    print(f"Notice: Game between {game.player1.username} and {game.player2.username} finished.")
    return
  
  def update_statistics(self, game: GameController) -> None:
    """
    Updates player statistics based on the results of a completed game.

    Arguments:
      game: GameController - the completed game to update statistics for
    """
    assert(game.is_game_over())
    player1, player2 = game.player1.username, game.player2.username
    results = game.get_results()
    self.statistics[player1]["played"] += 1
    self.statistics[player2]["played"] += 1
    # Handle outcome
    winner = results[0]
    # If winner is None, the game was a tie
    if not winner:
      self.statistics[player1]["tied"] += 1
      self.statistics[player2]["tied"] += 1
    else:
      loser = player2 if winner == player1 else player1
      self.statistics[winner]["won"] += 1
      self.statistics[loser]["lost"] += 1
    return

  def compute_status(self) -> Literal["running", "finished", "cancelled"]:
    """
    Returns:
      - "running" if the tournament is still running
      - "finished" if the tournament is finished
      - "cancelled" if the tournament was cancelled
    """
    if self.cancelled: return "cancelled"
    elif len(self.completed_games) != self.length: return "running"
    else: return "finished"

  def cancel(self) -> None:
    """
    Cancels the tournament.
    """
    status = self.compute_status()
    if status == "cancelled":
      print("Notice: tournament already cancelled.")
    elif status == "finished":
      print("Notice: tournament already finished.")
    else:
      print("Notice: cancelling tournament.")
      self.cancelled = True

  def print_rankings(self) -> None:
    """
    Prints out the ranking of players in a formatted fashion.
    """
    status = self.compute_status()
    rankings = rank_sort(self.statistics)
    if status == "cancelled":
      print("Notice: Tournament was cancelled.")
    else:      
      print(f"Notice: Tournament is currently {status}.\n")
      print(f"Rankings:\n")
      print("{:<15} {:<10} {:<5} {:<10} {:<5}".format('Username', 'Points', 'Wins', 'Losses', 'Ties'))
      for ranking in rankings:
        print("{:<15} {:<10} {:<5} {:<10} {:<5}".format(ranking['username'], ranking['points'], ranking['won'], ranking['lost'], ranking['tied']))

  async def available_wait(self) -> None:
    """
    Waits for a pair of players to be available.
    """
    while len(self.available_players) < 2:
      await asyncio.sleep(3)

async def run_tournament(players: dict[str, Player]) -> None:
  """
  Runs a complete round-robin tournament.

  Arguments:
    players: a dictionary mapping player usernames (strings) to unique Player objects
  """
  tournament = Tournament(players)
  if not tournament.cancelled:
    await tournament.start()
  return
