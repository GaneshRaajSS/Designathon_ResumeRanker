from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def compute_cosine_similarity(jd_embedding, profile_embeddings):
    jd_vec = np.array(jd_embedding).reshape(1, -1)
    profile_vecs = np.array([np.array(e) for e in profile_embeddings])
    return cosine_similarity(jd_vec, profile_vecs)[0]