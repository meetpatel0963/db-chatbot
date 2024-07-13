from gensim.summarization.bm25 import BM25


class PassageRetrieval:
  """
    To retrieve the top N passages from the given corpus.
    Each of these retrieved passages will be given as a context along with the user query into the AnswerExtractor Model.
    
    Retrieval Algorithm: BM25 (Best Matching)

    Given a query Q containing keywords q1, q2, ... , qn, the BM25 score of a document D is given by:

    score(D, Q) : SUM ( FOR EACH TERM IN THE QUERY => IDF(qi) * [ { f(qi, D) * (k1 + 1) } / { f(qi, D) + k1 * (1 - b + b * (|D| / avgDL ) } ] )

    where, IDF(qi) = Inverse document frequency weight of the query term qi,
           f(qi, D) = qi's term frequency in document D, 
           |D| = length of the document D in words,
           avgDL = average document length in text collection 
           k1 and b are free parameters : In absence of advanced optimization => k1 : [1.2, 2] and b : 0.75

    IDF(qi) = ln(( { N - n(qi) + 0.5 } / { n(qi) + 0.5 } ) + 1 )

    where, N = total number of docs in the collection,
           n(qi) = number of docs containing qi
  """
  
  # Initialize tokenize function 
  def __init__(self, nlp):
    # pass the given text though the Spacy NLP pipeline and extract the lemma of each token
    self.tokenize = lambda text: [token.lemma_ for token in nlp(text)]
    self.bm25 = None
    self.passages = None

  # Create an instance of BM25 with the given corpus
  def fit(self, docs):
    corpus = [self.tokenize(p) for p in docs]
    self.bm25 = BM25(corpus)
    self.passages = docs

  # Compute the scores of given query in relation to every passage in the corpus and return the top N passages
  def most_similar(self, question, topn=4):
    tokens = self.tokenize(question)
    average_idf = sum(float(val) for val in self.bm25.idf.values()) / len(self.bm25.idf)
    scores = self.bm25.get_scores(tokens, average_idf)
    pairs = [(s, i) for i, s in enumerate(scores)]
    pairs.sort(reverse=True)
    passages = [self.passages[i] for _, i in pairs[:topn]]
    return passages

