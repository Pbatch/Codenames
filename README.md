# Codenames

## Description

* In Codenames two teams compete by each having a Spymaster give one word clues which can point to multiple words on the board. 
* The other players on the team attempt to guess their team's words while avoiding the words of the other team.
* In this project we demonstrate that a computer can successfully play the role of a good Spymaster.

## Explanation
* Word2vec is a model that takes a corpus of words and embeds it in a vector space, with similar words having a higher score under the cosine metric.

Note - The user must specify 'target', the number of words the model should aim to link
#### Simple mode
Idea - A clue is only as good as the worst word
1) Loop through all possible guesses  
2) Calculate the cosine similarity between the guess and all your words
3) Set ally score to be the minimum cosine similarity of the top 'target' words
4) Set the enemy score to be the largest cosine similarity between the guess and all the enemy words
5) Set guess score to the ally score minus the enemy score
#### Cluster mode
Idea -  Clues should be clusters of similar words,
rather than just words that link to a guess.
1) Loop through all possible guesses
2) For each cluster of size 'target' of blue words
3) Set ally score to be the sum of pairwise cosine similarities between words in the cluster and the guess (For comparison sake we divide by the size of the cluster here)
4) Set the enemy score to be the largest cosine similarity between the guess and all the enemy words
5) Set guess score to the ally score minus the enemy score
## Usage

* Example board  
* Example output  
* Custom usage
* Pre-trained word vectors - https://fasttext.cc/docs/en/english-vectors.html

## Current problems (and potential solutions)

Problem - Guesses too similar to board words  
Solution - Use stemming on board words and guesses

Problem - Guesses may rhyme with board words  
Solution - Insert good library here?

Problem - Not all Codenames words have word2vec representations  
Solution - Use fastText representations instead




