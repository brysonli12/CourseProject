
# A very simple Flask Hello World app for you to get started with...

from flask import Flask
from flask import request, render_template
import json
import time
from nltk.corpus import stopwords
from rank_bm25 import BM25Okapi

stop_words = set([token.lower for token in stopwords.words('english')])

app = Flask(__name__)
messages = {'query': "Web App Development", "results":[{'title': 'Message One',
             'content': 'Message One Content'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]}

@app.route('/', methods = ['GET', 'POST'])
def index():
    text = str(request.args.get('input'))

    try:
        return render_template('index.html') #'Hello from Flask! + input is ' + str(text)
    except Exception as e:
        return str(e)

@app.route('/about', methods = ['GET'])
def about():
    try:
        return render_template('about.html')
    except Exception as e:
        return str(e)

@app.route('/add_doc', methods = ['GET', 'POST'])
def add_doc():
    #text = str(request.args.get('
    # request.form
    # request.data
    """expected request:
    {
        'url': '<url of page>',
        'title': '<title of page>'
        'summary': 'user generated summary/excerpt'
        # maybe a tag or something
    }
    each document/article saved based on timestamp
    """
    import time
    curr_time = time.time()
    #return str(request.form)
    try:
        f = open('/home/brysonli/mysite/data/data' + str(curr_time) + ".txt", 'w')
        f.write(request.form['source_url'])
        f.write('\n')
        f.write(request.form['page_title'])
        f.write('\n')
        f.write(request.form['explanation'] + " ~ " + request.form['highlighted_text'])

        #data = request.get_json()
        return {'message':'Successful!'}
    except Exception as e:
        return {'message': str(e)}

# the page with the form to search
@app.route('/search_page', methods = ['GET', 'POST'])
def search_page():
    try:
        a = request.get_json()["url"]
    except Exception as e:
        a = str(e)
    return '.Hello from Flask! data { ' + a  + "?" + str(request.data) + " | " + str(request.form)


@app.route('/search', methods = ['GET', 'POST'])
def search():
    # return the link to the search results
    try:
        return {"redirect_url": "https://brysonli.pythonanywhere.com/results?query=%s" % request.form["dl_search_query"]}
    except Exception as e:
        return str(e)

# the page with the results/details for one page
@app.route('/results', methods = ['GET', 'POST'])
def result():
    # allow searching using the arguments
    text = request.args.get('query', None)
    # or searching using the form results (from the website)
    # prioritize the form (in case users enters more queries here)
    if 'query' in request.form:
        results = search_for_query(request.form['query'])
    else: # then the arguments
        results = search_for_query(text)


    try:
        return render_template('results.html', messages=results) #'Hello from Flask! + input is ' + str(text)
    except Exception as e:
        return str(e)

def get_num_docs():
    # return number of docs stored
    import os
    count = 0
    for root_dir, cur_dir, files in os.walk(r'/home/brysonli/mysite/data'):
        count += len(files)
        print('file count:', count)
    return count

def search_for_query(search_for):
    # return list of messages with the following format:
    """{'query': "Web App Development", "results":[{'title': 'Message One',
             'content': 'Message One Content'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]}
    """

    messages = {'query': search_for, "results":[{'title': search_for + 'Message One',
             'content': 'Message One Content'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]}

    try:
        from nltk.tokenize import TreebankWordTokenizer
        import os
        messages_no_result = {'query': search_for, "results":[{'title': "No results",
                 'content': 'no results found for your search'}]}
        msg_list = []

        titles = []
        urls = []
        doc_list = []
        doc_ct = 0
        # load all docs
        for root_dir, cur_dir, files in os.walk(r'/home/brysonli/mysite/data'):

            for f in files:
                curr_doc = ""
                opened_doc = open(root_dir + '/' + f, 'r')
                url = False
                title = False
                for line in opened_doc:
                    if not url:
                        urls.append(line.strip())
                        url = True
                    elif not title:
                        titles.append(line.strip())
                        title = True
                    else:
                        curr_doc = curr_doc + str(line.strip())
                doc_list.append(curr_doc)
                #misc_info.append([title, url])
                doc_ct += 1

        # tokenize them
        #from nltk.tokenize import word_tokenize
        tokenizer = TreebankWordTokenizer() # word_tokenize#
        tokenized_docs = [tokenizer.tokenize((titles[doc] + " " + doc_list[doc]).lower()) for doc in range(len(doc_list))]

        # stop word removal?

        # bm25 search
        bm25 = BM25Okapi(tokenized_docs)

        search_tokenized = tokenizer.tokenize(search_for.lower())

        # rank
        doc_scores = bm25.get_scores(search_tokenized)
        # doc list
        # tokenized_docs
        results_display = [(x,y,z,a) for (x, y, z, a) in sorted(zip(doc_scores, doc_list, titles, urls), key=lambda triple:triple[0], reverse=True)]
        result_num = 1


        for r in results_display:
            msg_list.append({'title': ('Result %d : %s ' % (result_num, r[2])) + " ~ Score: " + str(r[0]),
                'url': r[3],
                 'content': str(r[1])[:min(len(r[1]), 500)]+"..."})
            result_num += 1
    except Exception as e:
        msg_list.append({'title': 'Error message', 'url': 'http://brysonli.pythonanywhere.com/', 'content': str(e)})
    messages = {'query': search_for, "results":msg_list}
    return messages


# topic extraction
@app.route('/topics', methods = ['GET', 'POST'])
def topics():
    try:
        import os
        import traceback
        titles = []
        urls = []
        doc_list = []
        doc_ct = 0
        # load all docs
        for root_dir, cur_dir, files in os.walk(r'/home/brysonli/mysite/data'):

            for f in files:
                curr_doc = ""
                opened_doc = open(root_dir + '/' + f, 'r')
                url = False
                title = False
                for line in opened_doc:
                    if not url:
                        urls.append(line.strip())
                        url = True
                    elif not title:
                        titles.append(line.strip())
                        # title could contribute to the topic
                        curr_doc = line.strip()
                        title = True
                    else:
                        curr_doc = curr_doc + " " + str(line.strip())
                doc_list.append(curr_doc)
                #misc_info.append([title, url])
                doc_ct += 1
                #text = str(request.args.get('
    # request.form
    # request.data
    # Author: Olivier Grisel <olivier.grisel@ensta.org>
    # License: Simplified BSD
    # https://ogrisel.github.io/scikit-learn.org/sklearn-tutorial/auto_examples/applications/topics_extraction_with_nmf.html
        from sklearn.feature_extraction import text
        from sklearn import decomposition
        from time import time
        n_samples = get_num_docs() - 1
        n_features = 1000
        n_topics = 10
        n_top_words = 20


        t0 = time()
        #print "Loading dataset and extracting TF-IDF features..."
        dataset = doc_list

        vectorizer = text.CountVectorizer(max_df=0.95, max_features=n_features)
        counts = vectorizer.fit_transform(dataset[:n_samples])
        tfidf = text.TfidfTransformer().fit_transform(counts)
        #print "done in %0.3fs." % (time() - t0)

        # Fit the NMF model
        #print "Fitting the NMF model on with n_samples=%d and n_features=%d..." % (
        #    n_samples, n_features)
        nmf = decomposition.NMF(n_components=n_topics).fit(tfidf)
        #print "done in %0.3fs." % (time() - t0)

        # Inverse the vectorizer vocabulary to be able
        feature_names = vectorizer.get_feature_names()
        topics = []
        for topic_idx, topic in enumerate(nmf.components_):
            # "Topic #%d:" % topic_idx
            topics.append({"number": "Topic %d" % ((topic_idx)+1), "topic_list": " ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])})
    except Exception as e:
        return str(e) # str(traceback.format_exc()) #
    try:
        return render_template('topics.html', messages={'topics': topics}) #'Hello from Flask! + input is ' + str(text)
    except Exception as e:
        return str(e)