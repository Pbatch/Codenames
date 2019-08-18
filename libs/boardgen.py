import numpy as np
import argparse


class Boardgen:
    def __init__(self, in_file):

        self.in_file = in_file
        self.board = self.generate_board()

    def generate_board(self):
        """
        Create a game board
        """
        try:
            all_words = [word.strip().lower() for word in open(self.in_file)]
        except UnicodeDecodeError:
            raise Exception("Make sure that in_file is a text file")
        except FileNotFoundError:
            raise Exception("Make sure that in_file exists")

        permutation = np.random.permutation(len(all_words))
        words = np.array(all_words)[permutation][:25]

        # 9 Blue, 8 Red, 7 Neutral, 1 Assassin
        board = []
        for i, word in enumerate(words):
            if i < 9:
                type = "blue"
                colour = "#0080FF"
            elif i < 17:
                type = "red"
                colour = "#FF0000"
            elif i < 24:
                type = "neutral"
                colour = "#D0D0D0"
            else:
                type = "assassin"
                colour = "#202020"
            word_details = {"name": word, "type": type, "colour": colour, "active": False}
            board.append(word_details)

        np.random.shuffle(board)
        return board


def main():
    parser = argparse.ArgumentParser(description='Create a Codenames board from a set of words')
    parser.add_argument('codenames_words', type=str,
                        help='The file location of Codenames words')
    parser.add_argument('-seed', type=int, default=None,
                        help='Seed for the random board generation')
    args = parser.parse_args()
    _ = Boardgen(args.codenames_words, args.seed)


if __name__ == "__main__":
    main()