



def find_similar_question(self, question: str,faq:list ,similarity_threshold: float = 0.8) -> Tuple[str, str, float]:
    if self.qa_data.empty:
        return None, None, None
    query_embedding = self.model.encode(question, convert_to_tensor=True)
    stored_questions = faq.mapped("questions")
    stored_question_embeddings = self.model.encode(stored_questions, convert_to_tensor=True)

    # Compute cosine similarities
    similarities = util.pytorch_cos_sim(query_embedding, stored_question_embeddings)

    # Find the most similar question based on similarity threshold
    max_similarity, idx = torch.max(similarities, dim=1)
    if max_similarity.item() >= similarity_threshold:
        return self.qa_data.iloc[idx.item()]['Question'], self.qa_data.iloc[idx.item()]['Answer'], 0.0

    return None, None, None