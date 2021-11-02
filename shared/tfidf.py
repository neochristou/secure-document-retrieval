import os
import pickle

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

docs = []
titles = []

for filename in os.listdir("./Gutenberg/txt/"):
    f = open("./Gutenberg/txt/" + filename, 'r')
    try:
        data = f.read()
        docs.append(data)
        titles.append(filename)
    except:
        pass
    f.close()

vectorizer = TfidfVectorizer(
    max_df=.65, min_df=1, stop_words=None, use_idf=True, norm=None)
tf_idf = vectorizer.fit_transform(docs)
# transformed_documents_as_array = tf_idf.toarray()

# print(vectorizer.get_feature_names())

# pickle.dump(tf_idf, open("tfidf.pickle", "wb"))

# print(transformed_documents_as_array)


# # construct a list of output file paths using the previous list of text files the relative path for tf_idf_output
# output_filenames = ["tf_idf_output/" + title for title in titles]

# loop each item in transformed_documents_as_array, using enumerate to keep track of the current position
# for counter, doc in enumerate(transformed_documents_as_array):
#     # construct a dataframe
#     tf_idf_tuples = list(zip(vectorizer.get_feature_names(), doc))
#     one_doc_as_df = pd.DataFrame.from_records(tf_idf_tuples, columns=[
# 'term', 'score'])

#     # output to a csv using the enumerated value for the filename
#     one_doc_as_df.to_csv(output_filenames[counter])
