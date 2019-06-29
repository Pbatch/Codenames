# Codenames

#### Description

* In Codenames two teams compete by each having a Spymaster give one word clues which can point to multiple words on the board. 
* The other players on the team attempt to guess their team's words while avoiding the words of the other team.
* In this project we demonstrate that a computer can successfully play the role of a good Spymaster.

#### Explanation
* Word2vec is a model that takes a corpus of words and embeds it in a vector space, with similar words being closer under the cosine metric.
* For each possible guess we can use these distances to generate a score.

Note - The user must specify 'target', the number of words the model should aim to link
##### Simple mode
Idea - A clue is only as good as the worst word  
1) Calculate the similarity scores for all the words in blue
2) Set the blue score to be the minimum score of the top 'target' words
##### Cluster mode
Idea -  Clues should be clusters of similar words,
rather than just words that link to a guess.
1) Calculate a score for each cluster of size 'target' of blue words
2) This score is the sum of pairwise connections in the cluster divided by the cluster size
#### Usage

* Example board  
* Example output  
* Custom usage
* Pre-trained word vectors - https://fasttext.cc/docs/en/english-vectors.html

#### Current problems (and potential solutions)

Problem - Guesses too similar to board words  
Solution - Use stemming on board words and guesses

Problem - Guesses may rhyme with board words  
Solution - Insert good library here?

Problem - Not all Codenames words have word2vec representations  
Solution - Use fastText representations instead




