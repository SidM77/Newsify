import requests
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from bs4 import BeautifulSoup
from heapq import nlargest

def procedure(query):
    urls = get_article(query)
    s = len(urls)
    title = ""
    if s < 5 :
        for i in range(0,s):
            title = get_title(urls[i])
            print(f"{i+1}. {title}")
    else:
        for i in range(0,5):
            title = get_title(urls[i])
            print(f"{i+1}. {title}")
    print()
    news_no = int(input("Enter your News number: "))
    print()
    article_info = extract_article_info(urls[news_no - 1])
    print("TITLE: ", end="")
    print(article_info['title'])
    print()

    summary = summarize(article_info['content'])
    print(summary)
    print(urls[news_no-1])


def get_title(url):
    r = requests.get(url)
    htmlContent = r.content
    soup = BeautifulSoup(htmlContent, 'html.parser')
    title = soup.find('h1', {"class": "sp-ttl"})
    if title is not None:
        return title.string.strip()
    else:
        return None

def get_article(query):
    api_key = '60daf5b9d1bf49418a61970603fbc739'
    url = 'https://newsapi.org/v2/everything'

    # Set up the request headers and parameters
    headers = {'Authorization': f'Bearer {api_key}'}
    params = {'q': query, 'pageSize': 10, 'domains': 'ndtv.com'}

    # Send the request and get the response
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    # Extract the article URLs
    articles = data['articles']
    urls = [article['url'] for article in articles if 'ndtv.com' in article['url']]
    # print(urls)
    return urls


def extract_article_info(url):
    r = requests.get(url)
    htmlContent = r.content
    soup = BeautifulSoup(htmlContent, 'html.parser')

    article_info = {}

    # Extract the article title
    title = soup.find('h1', {"class": "sp-ttl"})
    if title is not None:
        article_info['title'] = title.string.strip()

    # Extract the headline
    desc = soup.find('h2', {"class": "sp-descp"})
    if desc is not None:
        article_info['headline'] = desc.string.strip()

    # Extract the article content
    text = ""
    ps = soup.find_all('p')
    for i in range(len(ps)):
        if ps[i] is not None and ps[i].string is not None:
            text += " " + ps[i].string.strip()
    article_info['content'] = text.strip()

    return article_info


nlp = spacy.load('en_core_web_sm')
stopwords = list(STOP_WORDS)
punctuation = punctuation + '\n'


def summarize(text):
    docs = nlp(text)
    tokens = [token.text for token in docs]

    # checking word frequency
    word_frequecy = {}
    for word in docs:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text not in word_frequecy.keys():
                word_frequecy[word.text] = 1
            else:
                word_frequecy[word.text] += 1

    # check max frequency
    max_frequency = max(word_frequecy.values())

    # getting frequency divided by max frequency
    for word in word_frequecy.keys():
        word_frequecy[word] = word_frequecy[word] / max_frequency

    # tokens of sentence are made
    sentence_tokens = [sent for sent in docs.sents]

    # score of sentence is calculated
    sentence_score = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequecy.keys() and len(sent.text.split(' ')) < 30:
                if sent not in sentence_score.keys():
                    sentence_score[sent] = word_frequecy[word.text.lower()]
                else:
                    sentence_score[sent] += word_frequecy[word.text.lower()]

    # percentage of summary is made
    select_length = int(len(sentence_tokens) * 0.3)
    summary = nlargest(select_length, sentence_score, key=sentence_score.get)

    # final part the summary is joined
    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)

    return summary

print("""
*** CHOOSE YOUR OPTION ***
1. CURRENT AFFAIRS
2. BUSINESS AND FINANCE
3. POLITICS
4. SCIENCE AND TECHNOLOGY
5. ENTERTAINMENT
6. SPORTS
7. ENTER YOUR OWN QUERY
""")
choice = input("Enter your choice: ")
print()

if(choice == '1'):
    query = 'current affairs'
    procedure(query)

elif(choice == '2'):
    query = 'business and finance'
    procedure(query)

elif(choice == '3'):
    query = 'politics'
    procedure(query)


elif(choice == '4'):
    query = 'science and technology'
    procedure(query)


elif(choice == '5'):
    query = 'bollywood and hollywood'
    procedure(query)


elif(choice == '6'):
    query = 'cricket and football'
    procedure(query)

elif(choice == '7'):
    query = input("Enter your own query: ")
    procedure(query)

else:
    print("Enter Valid choice !!!")
