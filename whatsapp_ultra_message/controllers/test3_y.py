
import numpy as np
import json


def deserialize_vectors_data(filename="vectors.json"):
	with open(filename, "r") as f:
		data = json.load(f)
	vectors = np.array(data["vectors"], dtype = np.float32)
	documents = data["documents"]

	return vectors, documents


if __name__ == "__main__":
    vectors, documents = deserialize_vectors_data("vectors.json")
    print("Number of vectors:", len(vectors))
    print("First document:", documents[0])