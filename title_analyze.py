import re, nltk
from nltk.corpus import wordnet
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer

def wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def tokenize(s):
    word_single = WordNetLemmatizer()
    tokens = nltk.word_tokenize(s)
    pos_tag = [pos[1] for pos in nltk.pos_tag(tokens)]
    roots = [stemmer.lemmatize(word, wordnet_pos(pos_tag[idx])) for idx, word in enumerate(tokens)]
    roots = [word_single.lemmatize(x.lower()) for x in roots if word_re.match(x)]
    roots = filter(lambda x: x not in stop_words, roots)
    return list(roots)


def get_title_list():
    fp = open('data/q_bio/new_all.enw', 'r', encoding='utf8')
    title_list = []
    for line in fp.readlines():
        if '%T' in line:
            title_list.append(line.replace('%T', '').strip(' '))
    return title_list


def dump(name:str):
    with open(name, 'w', encoding='utf8') as fp:
        for key in word_frequency:
            fp.write(f'{key}: {word_frequency[key]}\n')


if __name__ == '__main__':
    stemmer = nltk.stem.WordNetLemmatizer()
    word_re = re.compile(r'^[a-zA-Z0-9]*$')
    stop_words = set(nltk.corpus.stopwords.words('english'))
    words = []
    target_title = []

    title = get_title_list()
    for item in title:
        part = tokenize(item)
        if 'cancer' in part and 'image' in part:
            print(item)
    word_frequency = FreqDist(words)
    print(word_frequency.most_common(50))
    with open('title.txt', 'w') as fp:
        for i in target_title:
            fp.write(i)


