import numpy as np


class Computer:
    """
    Generate a random sequence of computer moves
    """
    def __init__(self, board):
        """
        Parameters
        ----------
        board: json
            The current board state
        """
        self.board = board
        self.distribution = self.get_distribution()
        self.blue, self.red, self.neutral = self.get_types()

    def get_types(self):
        """
        Extract the types from the cards
        """
        blue = []
        red = []
        neutral = []
        for card in self.board[1:]:
            card_id = card["id"]
            if card["type"] == "blue" and not card["active"]:
                blue.append(card_id)
            if card["type"] == "red" and not card["active"]:
                red.append(card_id)
            if card["type"] == "neutral" and not card["active"]:
                neutral.append(card_id)
        return blue, red, neutral

    def get_distribution(self):
        """
        Get the distribution over the classes depending on the difficulty
        """
        if self.board[0]["difficulty"] == "easy":
            distribution = {"blue": 1, "red": 2, "neutral": 1, "none": 3}
        elif self.board[0]["difficulty"] == "medium":
            distribution = {"blue": 1, "red": 2, "neutral": 1, "none": 2}
        else:
            distribution = {"blue": 0, "red": 3, "neutral": 1, "none": 2}
        return distribution

    def generate_computer_sequence(self):
        """
        Generate a sequence for the computer
        """

        sequence = []
        card_type = None
        decay = 1
        while card_type not in {"blue", "neutral"}:
            if len(self.blue) + len(self.red) + len(self.neutral) == 0:
                break
            weights = [self.distribution["red"]*decay if len(self.red) > 0 else 0,
                       self.distribution["blue"] if len(self.blue) > 0 else 0,
                       self.distribution["neutral"] if len(self.neutral) > 0 else 0,
                       self.distribution["none"] if len(sequence) != 0 else 0]
            weights = np.array(weights) / sum(weights)

            card_type = np.random.choice(["red", "blue", "neutral", "none"], p=weights)

            if card_type == "red":
                card_id = np.random.choice(self.red)
                self.red.remove(card_id)

            elif card_type == "blue":
                card_id = np.random.choice(self.blue)
                self.blue.remove(card_id)

            elif card_type == "neutral":
                card_id = np.random.choice(self.neutral)
                self.neutral.remove(card_id)

            else:
                break

            sequence.append(int(card_id))
            decay *= 0.35

        return sequence
