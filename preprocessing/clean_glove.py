from tqdm import tqdm
import numpy as np
from numba import njit
from gensim.parsing.preprocessing import stem
from pattern3.text.en.inflect import singularize, pluralize
import pickle
from copy import deepcopy


class CleanGlove:
    def __init__(self, glove_path, codenames_path, stopwords_path, threshold=0.5, limit=int(3e5)):
        """
        :param glove_path: str
                         : The path to the glove vectors
        :param codenames_path: str
                             : The path to the codenames words
        :param stopwords_path: str
                             : The path to the stopwords
        :param threshold: float (default = 0.5)
                        : The similarity threshold for the dot product between vectors
        :param limit: int (default = int(3e5))
                    : The number of glove vectors to parse
        """
        self.glove_path = glove_path
        self.codenames_path = codenames_path
        self.stopwords_path = stopwords_path
        self.threshold = threshold
        self.limit = limit

        self.stopwords = None
        self.codenames_words = None
        self.stemmed_codenames_words = None
        self.codenames_vectors = None
        self.relevant_words = None
        self.relevant_vectors = None

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

    def _valid_word(self, word):
        """
        Check if the given word is valid
        """
        # Stopwords check
        if word in self.stopwords:
            return False

        # Punctuation check
        if not word.isalpha():
            return False

        # Accent check
        if not word.isascii():
            return False

        # Vowel + y check
        if set("aeiouy").isdisjoint(word):
            return False

        # Length check
        if not 2 <= len(word) <= 12:
            return False

        # Plural check
        if pluralize(word) in self.codenames_words:
            return False

        # Singular check
        if singularize(word) in self.codenames_words:
            return False

        # Stem check
        if stem(word) in self.stemmed_codenames_words:
            return False

        # Containment check
        for codenames_word in self.codenames_words:
            if codenames_word in word or word in codenames_word:
                return False

        return True

    def _get_codenames_words(self):
        """
        Get the codenames words
        """
        codenames_words = set(word.strip('\n').replace(" ", "") for word in open(self.codenames_path))
        self.codenames_words = codenames_words
        self.stemmed_codenames_words = set(map(stem, codenames_words))

    def _get_stopwords(self):
        """
        Get the stopwords
        """
        stopwords = set(word.strip('\n').replace(" ", "") for word in open(self.stopwords_path))
        self.stopwords = stopwords

    def _get_codenames_word_vectors(self):
        """
        Get the vectors for the codenames words
        """
        codenames_vectors = {}
        with open(self.glove_path, 'r', encoding='utf8') as f:
            for line in tqdm(f):
                word_and_vec = line.strip().split(' ')
                word = word_and_vec[0]
                if word in self.codenames_words:
                    vec = np.array(word_and_vec[1:], dtype=np.float32)
                    codenames_vectors[word] = vec
                    if len(codenames_vectors) == len(self.codenames_words):
                        break
        self.codenames_vectors = codenames_vectors

    def _get_relevant_words_and_vectors(self):
        """
        Get the words relevant to the codenames words
        """
        relevant_words = {w: [] for w in self.codenames_words}
        relevant_vectors = deepcopy(self.codenames_vectors)
        with open(self.glove_path, 'r', encoding='utf8') as f:
            for _ in tqdm(range(self.limit)):
                line = f.readline().strip()
                word_and_vec = line.split(' ')
                word = word_and_vec[0]
                if not self._valid_word(word):
                    continue
                vec = np.array(word_and_vec[1:], dtype=np.float32)
                for codenames_word, codenames_vec in self.codenames_vectors.items():
                    cosine_similarity = self._cosine_similarity(codenames_vec, vec)
                    if cosine_similarity > self.threshold:
                        relevant_words[codenames_word].append(word)
                        if word not in relevant_vectors:
                            relevant_vectors[word] = vec

        self.relevant_words = relevant_words
        self.relevant_vectors = relevant_vectors

    def _save_relevant_words_and_vectors(self):
        """
        Save the relevant words and vectors
        """
        with open('relevant_words', 'wb') as f:
            pickle.dump(self.relevant_words, f)
        with open('relevant_vectors', 'wb') as f:
            pickle.dump(self.relevant_vectors, f)

    def run(self):
        """
        Run the pipeline
        """
        self._get_codenames_words()
        self._get_stopwords()
        self._get_codenames_word_vectors()
        self._get_relevant_words_and_vectors()
        self._save_relevant_words_and_vectors()


def main():
    cls = CleanGlove(glove_path='glove.42B.300d.txt',
                     codenames_path='../static/data/codenames_words',
                     stopwords_path='stopwords',
                     threshold=0.45,
                     limit=int(5e4))
    cls.run()


if __name__ == '__main__':
    main()
