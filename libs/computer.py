import numpy as np
from copy import deepcopy


class Computer:
    def __init__(self, board):
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
            name = card["name"].replace(" ", "")
            if card["type"] == "blue" and not card["active"]:
                blue.append(name)
            if card["type"] == "red" and not card["active"]:
                red.append(name)
            if card["type"] == "neutral" and not card["active"]:
                neutral.append(name)
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

    def make_computer_choices(self):
        """
        Perform a sequence of computer choices
        """
        board = deepcopy(self.board)

        sequence = []
        card_type = None
        decay = 1
        while card_type not in {"blue", "neutral"} and board[0]["red_remaining"] > 0:
            if len(self.blue) + len(self.red) + len(self.neutral) == 0:
                break
            weights = [self.distribution["red"]*decay if len(self.red) > 0 else 0,
                       self.distribution["blue"] if len(self.blue) > 0 else 0,
                       self.distribution["neutral"] if len(self.neutral) > 0 else 0,
                       self.distribution["none"] if len(sequence) != 0 else 0]
            weights = np.array(weights) / sum(weights)
            print(weights)

            card_type = np.random.choice(["red", "blue", "neutral", "none"], p=weights)

            if card_type == "red":
                name = np.random.choice(self.red)
                self.red.remove(name)

            elif card_type == "blue":
                name = np.random.choice(self.blue)
                self.blue.remove(name)

            elif card_type == "neutral":
                name = np.random.choice(self.neutral)
                self.neutral.remove(name)

            else:
                break

            sequence.append(name)
            decay *= 0.35

        board[0]["sequence"] = sequence

        if len(sequence) != 0:
            board[0]["state"] = "computer_turn"
        else:
            board[0]["state"] = "choose_clue"

        return board


def main():
    import boardgen
    board = boardgen.Boardgen("../static/data/codenames_words").board
    board.insert(0, {"clue": "",
                     "target": 0,
                     "red_remaining": 8,
                     "blue_remaining": 9,
                     "neutral_remaining": 7,
                     "difficulty": "hard",
                     "computer_turn": True
                     })
    print(board)
    new_board = Computer(board).make_computer_choices()
    print(new_board)


if __name__ == "__main__":
    main()

