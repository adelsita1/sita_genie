from flask import Flask,request,jsonify
import json
import requests
app=Flask(__name__)
import spacy
model = spacy.load('en_core_web_md')
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

    # @http.route('/spacy', type="json", auth="public", website=True, method=['POST','GET'])
@app.route('/spacy', methods=['POST'])
def get_similarity(**kw):
    # print("kw/",kw)
    data = request.json
    print("data",data)
    query=data['query']
    questions=data['questions']
    answers=data['answers']
    print("query",query)

    top_n=4
    question_vectors = train_model(questions)
    query_vector = get_sentence_vector(preprocess_text(query))
    similarities = cosine_similarity([query_vector], question_vectors).flatten()
    # print("similarities1", similarities)
    # similarities = query_vector.similarity(question_vectors)
    # print("similarities2",similarities)
    top_indices = similarities.argsort()[-top_n:][::-1].tolist()
    # print("questions[i]", questions[top_indices])
    # print("answer[i]", answers[top_indices])
    print("top_indices", top_indices)
    print("top_indices", type(top_indices))

    results = []
    for i in top_indices:
        print("questions[i]",questions[i])
        print("sim[i]",similarities[i])
        # qa_record = qa_records[i]
        if similarities[i] <0.8:
            continue
        results.append({
            'question': questions[i],
            'answer': answers[i],
            'similarity': similarities[i].tolist(),
        })
    print("results hereee", results)
        # Increment the call count
        # qa_record.number_of_calls += 1
        # qa_record.similar_questions = qa_record.similar_questions + str(query) + '\n' if str(
        #     query) not in qa_record.similar_questions else qa_record.similar_questions

    return jsonify(results)
def get_sentence_vector(text):
    doc = model(text)
    return doc.vector


def train_model(questions):
    question_vectors = np.array([get_sentence_vector(preprocess_text(q)) for q in questions])
    return question_vectors


def preprocess_text(text):
    doc = model(text)
    return " ".join([token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct])


if __name__ == '__main__':
    app.run(debug=True)