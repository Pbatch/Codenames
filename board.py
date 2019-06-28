import numpy as np
from colorama import Fore
from colorama import Style
import argparse


class Board:
    def __init__(self, in_file, print_board=False):

        self.in_file = in_file
        self.board, self.blue, self.red, self.neutral, self.assassin \
            = self.generate_board()
        if print_board:
            self.print_board()

    def get_board_and_classes(self):
        """
        Get the board and the class of each word
        """
        return self.board, self.blue, self.red, self.neutral, self.assassin

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
        shuffled_all_words = np.array(all_words)[permutation]
        board = shuffled_all_words[:25]

        # Permute the board for printing purposes, it makes the game look more 'random'
        board_permutation = np.random.permutation(25)
        try:
            tmp_board = np.array(board)[board_permutation]
        except IndexError:
            raise Exception("The in_file must contain at least 25 words")

        # 9 Blue, 8 Red, 7 Neutral, 1 Assassin
        blue = tmp_board[:9]
        red = tmp_board[9:17]
        neutral = tmp_board[17:24]
        assassin = tmp_board[24]

        return board, blue, red, neutral, assassin

    def print_board(self):
        """
        Print the game board
        """

        # Set the formatting length to be: len("(ASSASSIN)") + longest_word_length
        longest_word_length = max(map(len, self.board))
        formatting_length = longest_word_length + 10

        for index, word in enumerate(self.board):
            if word in self.blue:
                word_to_print = word.upper() + "(BLUE)"
                print(f"{Fore.BLUE}{word_to_print: <{formatting_length}}{Style.RESET_ALL}", end="")
            elif word in self.red:
                word_to_print = word.upper() + "(RED)"
                print(f"{Fore.RED}{word_to_print: <{formatting_length}}{Style.RESET_ALL}", end="")
            elif word in self.neutral:
                word_to_print = word.upper() + "(NEUTRAL)"
                print(f"{Fore.WHITE}{word_to_print: <{formatting_length}}{Style.RESET_ALL}", end="")
            elif word in self.assassin:
                word_to_print = word.upper() + "(ASSASSIN)"
                print(f"{Fore.BLACK}{word_to_print: <{formatting_length}}{Style.RESET_ALL}", end="")
            # Go to a new line so that the grid is square
            if (index+1) % 5 == 0:
                print("\n")


def main():
    parser = argparse.ArgumentParser(description='Create a Codenames board from a set of words')
    parser.add_argument('codenames_words', type=str,
                        help='The file location of Codenames words')
    parser.add_argument('-print_board', type=bool,
                        help='Set to False if you do not want to print the board.'
                             'The colours might fail in a terminal', default=True)
    args = parser.parse_args()
    _ = Board(args.codenames_words, args.print_board)


if __name__ == "__main__":
    main()