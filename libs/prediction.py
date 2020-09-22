from itertools import chain
import pickle
import numpy as np
from numba import njit


@njit(fastmath=True)
def binary_search(arr):
    """
    Binary search
    """
    mini, mid, maxi = 0, 0, arr.shape[0]
    rand = arr[-1] * np.random.random()
    while mini < maxi:
        mid = mini + ((maxi - mini) >> 1)
        if rand > arr[mid]:
            mini = mid + 1
        else:
            maxi = mid
    return mini


class Predictor:
    """
    Generate clues for the blue team
    """
    def __init__(self,
                 relevant_words_path,
                 relevant_vectors_path,
                 board,
                 invalid_guesses,
                 alpha=1.0,
                 eta=0.4,
                 trials=1000):
        """
        Parameters
        ----------
        relevant_words_path: str
                          : The path to the dictionary of relevant words
        relevant_vectors_path: str
                             : The path to the dictionary of relevant vectors
        board: json
             : The current board state
        invalid_guesses: set
                       : Clues which have already been given
        alpha: float (default = 1.0)
             : The first parameter to the logistic function
        eta: float (default = 0.4)
           : The second parameter to the logistic function
        trials: int (default = 1000)
              : The number of trials to use for the Monte-Carlo method
        """
        self.relevant_words_path = relevant_words_path
        self.relevant_vectors_path = relevant_vectors_path
        self.board = board
        self.invalid_guesses = invalid_guesses
        self.alpha = alpha
        self.eta = eta
        self.trials = trials

        self.inactive_words = None
        self.words = None
        self.blue, self.red, self.neutral, self.assassin = None, None, None, None
        self.valid_guesses = None

    @staticmethod
    @njit(fastmath=True)
    def _cosine_similarity(u, v):
        """
        Calculate the cosine similarity between vectors u and v
        """
        u_dot_v = 0
        u_norm = 0
        v_norm = 0
        for i in range(u.shape[0]):
            u_dot_v += u[i] * v[i]
            u_norm += u[i] * u[i]
            v_norm += v[i] * v[i]

        u_norm = np.sqrt(u_norm)
        v_norm = np.sqrt(v_norm)

        if (u_norm == 0) or (v_norm == 0):
            similarity = 1.0
        else:
            similarity = u_dot_v / (u_norm * v_norm)
        return similarity

    @staticmethod
    @njit(fastmath=True)
    def _calculate_expected_score(similarities, n_blue, trials):
        """
        Calculate the expected score with a Monte-Carlo method
        """
        expected_score = 0
        for _ in range(trials):
            trial_score = 0
            cumsum = np.cumsum(similarities)
            while True:
                sample = binary_search(cumsum)
                if sample < n_blue:
                    if sample == 0:
                        cumsum[sample] = 0
                    else:
                        difference = cumsum[sample] - cumsum[sample - 1]
                        cumsum[sample:] -= difference
                    trial_score += 1
                else:
                    break
            expected_score += trial_score
        expected_score /= trials
        return expected_score

    def _similarity(self, u, v):
        return 1 / (1 + np.exp(-self.alpha * (self._cosine_similarity(u, v) - self.eta)))

    def _get_words(self):
        """
        Extract the words from every card
        """
        all_words = [card["name"].replace(" ", "") for card in self.board]
        return all_words

    def _get_types(self):
        """
        Extract the types from the cards
        """
        blue = []
        red = []
        neutral = []
        assassin = ""
        for card in self.board:
            name = card["name"].replace(" ", "")
            if card["type"] == "blue" and not card["active"]:
                blue.append(name)
            if card["type"] == "red" and not card["active"]:
                red.append(name)
            if card["type"] == "neutral" and not card["active"]:
                neutral.append(name)
            if card["type"] == "assassin" and not card["active"]:
                assassin = name
        return blue, red, neutral, assassin

    def _get_valid_guesses(self):
        """
        Get the relevant valid guesses
        """
        with open(self.relevant_words_path, 'rb') as f:
            relevant_words = pickle.load(f)
        potential_guesses = set(chain.from_iterable(relevant_words[w] for w in self.blue))
        valid_guesses = potential_guesses.difference(self.invalid_guesses)

        return valid_guesses

    def _get_relevant_vectors(self):
        """
        Get the relevant vectors
        """
        with open(self.relevant_vectors_path, 'rb') as f:
            relevant_vectors = pickle.load(f)
        return relevant_vectors

    def _setup(self):
        """
        Setup the relevant data structures
        """
        self.relevant_vectors = self._get_relevant_vectors()
        self.words = self._get_words()
        self.blue, self.red, self.neutral, self.assassin = self._get_types()
        self.ordered_words = self.blue + self.red + [self.assassin] + self.neutral
        self.ordered_word_vectors = np.array([self.relevant_vectors[w] for w in self.ordered_words], dtype=np.float32)
        self.valid_guesses = self._get_valid_guesses()

    def _calculate_guess_score(self, guess):
        """
        Generate a score for a guess
        """
        guess_vector = self.relevant_vectors[guess]
        similarities = [self._similarity(guess_vector, v) for v in self.ordered_word_vectors]
        similarities = np.array(similarities, dtype=np.float32)
        score = self._calculate_expected_score(similarities, len(self.blue), self.trials)

        return score, guess

    def _get_targets(self, guess, modal_score):
        """
        Get the target words for a given guess and modal score
        """
        best_guess_vector = self.relevant_vectors[guess]
        blue_similarities = np.array([self._cosine_similarity(best_guess_vector, self.relevant_vectors[w])
                                      for w in self.blue])
        sorted_idx = np.argsort(-blue_similarities)
        best_blue = set(np.array(self.blue)[sorted_idx][:modal_score])

        # DEBUGGING
        print(np.array(self.blue)[sorted_idx][:5])

        targets = []
        for card in self.board:
            if card['name'].replace(' ', '') in best_blue:
                targets.append(card['id'])
        return targets

    def run(self):
        """
        Get the best clue, it's score (rounded up) and the words it is supposed to link to
        """
        self._setup()
        guess_scores = (self._calculate_guess_score(g) for g in self.valid_guesses)
        score, clue = max(guess_scores, key=lambda x: x[0])
        print(f'Clue:{clue}, Score:{score}')
        score = int(np.ceil(score))
        targets = self._get_targets(clue, score)

        return clue, score, targets
