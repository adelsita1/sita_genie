from sentence_transformers import SentenceTransformer, util

# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# List of documents
corpus = ['how many pools.', 'This is another example.', 'How is the weather today?']

# Generate embeddings for corpus
corpus_embeddings = model.encode(corpus, convert_to_tensor=True)

# Query text
query = 'is there any swimming pools?'
query_embedding = model.encode(query, convert_to_tensor=True)

# Compute similarity using cosine similarity
similarities = util.pytorch_cos_sim(query_embedding, corpus_embeddings)
print(similarities)
similarity_list = similarities[0].tolist()
most_similar_idx = similarity_list.index(max(similarity_list))
most_similar_doc = corpus[most_similar_idx]
similarity_score = similarity_list[most_similar_idx]

# Output the result
print(f"Most similar document: {most_similar_doc}")
print(f"Similarity score: {similarity_score}")

from gensim.models import Word2Vec
from gensim.utils import simple_preprocess

# Example corpus
# sentences = ["This is a sample sentence", "This is another sentence", "Yet another sentence"]
sentences = ['how many pools.', 'This is another example.', 'How is the weather today?']
# Preprocess the sentences
tokenized_sentences = [simple_preprocess(sentence) for sentence in sentences]

# Train a Word2Vec model
model = Word2Vec(tokenized_sentences, vector_size=100, window=5, min_count=1, workers=4)

# Find similarity between two words
similarity = model.wv.similarity('sample', 'sentence')
print("Similarity between 'sample' and 'sentence':", similarity)

# Find most similar words to a given word
most_similar = model.wv.most_similar('sample')
print(most_similar)