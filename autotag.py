import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


if __name__ == '__main__':
    csv = 'pixiv.csv'
    df = pd.read_csv(csv).fillna('null')

    tag_list = []
    for i,row in df.iterrows():
        tags = []
        for j in range(10):
            tag = row['tag'+str(j)]
            if tag != 'null':
                tags.append(tag)
        tag_str = ' '.join(tags)
        tag_list.append(tag_str)

    df['tag_str'] = tag_list

    test = ['艦これ','かわいい']
    test_str = ' '.join(test)

    vectorizer = TfidfVectorizer(use_idf=True)
    vecs = vectorizer.fit_transform(np.append(df['tag_str'].values,test_str))

    df['tag_vec'] = list(vecs.toarray()[:-1])
    test_vec = vecs.toarray()[-1]

    distance_list = []
    for i, row in df.iterrows():
        vec1 = test_vec
        vec2 = row['tag_vec']
        distance = cos_sim(vec1,vec2)
        distance_list.append(distance)

    df['distance'] = distance_list
    df = df.sort_values(by='distance',ascending=False)
    df = df[df['distance']<1.0][:10]

    all_tags = []
    for i, row in df.iterrows():
        tags = row['tag_str'].split(' ')
        for tag in tags:
            if tag not in all_tags and tag not in test:
                all_tags.append(tag)

    print(all_tags)