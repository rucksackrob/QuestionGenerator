import wikipedia
import nltk
import nltk.data
import re
import pprint
import sys

namedEntityToQuestionWordDictionary = {
    "PERSON" : "Who",
    "NORP" : "What",
    "FAC" : "Where", #not sure this shouldn't be what
    "ORG" : "What",
    "GPE" : "What", #this might be Where under some circumstances
    "LOC" : "Where",
    "PRODUCT" : "What",
    "EVENT" : "When", # this might be what
    "WORK_OF_ART" : "What",
    "LAW" : "What",
    "LANGUAGE" : "What",
    "DATE" : "When",
    "TIME" : "When",
    "PERCENT" : "How much", #these are not tested
    "MONEY" : "How much", #these are not tested
    "QUANTITY" : "How much", #these are not tested
    "ORDINAL" : "How much", #these are not tested
    "CARDINAL" : "How much", #these are not tested
}

def getQuestionWord(namedEntity):
    return namedEntityToQuestionWordDictionary.get(namedEntity, "What")

if len(sys.argv) == 1:
    print (sys.argv[0])
    print("please enter topic in command line:")
    print(" python wikireader.py [topic]")
else:
    wikiString = ""
    for argumentCounter in (1, len(sys.argv) - 1):   
        wikiString += sys.argv[argumentCounter] + ' '
    """ 
    code  for tokenization and pos tagging based on lesson here (includes some import statements at top): 
    https://textminingonline.com/dive-into-nltk-part-iii-part-of-speech-tagging-and-pos-tagger
    """
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    
    print("")
    #currently testing using single wikipedia page, extracting sentences, looking at first sentence
    topic = (wikipedia.page(wikiString))
    print("Topic: " + topic.title)
    sentenceTokenizedText = nltk.sent_tokenize(topic.summary)
    print("Summary Paragraph:")
    print(sentenceTokenizedText)
    print("")
    #single sentence version (for project)
    wordTokenizedSentence = nltk.word_tokenize(sentenceTokenizedText[0])
    print("Sentence to be converted (tokenized):")
    print(wordTokenizedSentence)
    print("")
    posTaggedWords = nltk.pos_tag(wordTokenizedSentence)
    print("POS Tagged Sentence:")
    print(posTaggedWords)
    print("")
    namedEntities = nltk.ne_chunk(posTaggedWords)
    print("Sentence with entity recognition:")
    print(namedEntities)
    print("")
    
    """  
    code for building noun phrases (including some import statements at top)
    based on presentation here: http://nbviewer.jupyter.org/github/lukewrites/NP_chunking_with_nltk/blob/master/NP_chunking_with_the_NLTK.ipynb
    and source here: https://github.com/lukewrites/NP_chunking_with_nltk
    citation: Linguistics 101 for Pythonistas: Why noun phrase chunking with the NLTK is awesome & useful. Luke Petschauer. Pycon 2015 Montreal QC
    """
    #for noun phrase regex patterns, may need to build iteratively as some patterns are more complex or not identified.
    phrasePatterns = """
    NP: {<DT>*<RBS|JJ|JJR|JJS|VBG>*<CD|NN|NNS|NNP|NNPS>+<IN>*<DT>*<RBS|JJ|JJR|JJS|VBG>*<CD|NN|NNS|NNP|NNPS>+<POS>*<RBS|JJ|JJR|JJS|VBG>*<CD|NN|NNS|NNP|NNPS>*<RB>*<VBN>*<IN>*<DT>*<CD|NN|NNS|NNP|NNPS>*<IN>*<DT>*<CD|NN|NNS|NNP|NNPS>*<,>*<NN|NNS|NNP|NNPS>*}
        {<DT>*<RBS|JJ|JJR|JJS|VBG>*<CD|NN|NNS|NNP|NNPS>+<POS>*<DT>*<RBS|JJ|JJR|JJS|VBG>*<CD|NN|NNS|NNP|NNPS>*<RB>*<VBN>*<IN>*<DT>*<CD|NN|NNS|NNP|NNPS>*<IN>*<DT>*<CD|NN|NNS|NNP|NNPS>*<,>*<CD|NN|NNS|NNP|NNPS>*} 
    VP: {<V.*>*<TO>*<V.*>+}
    """
    phraseChunker = nltk.RegexpParser(phrasePatterns)

    #single sentence version of phrase chunking
    wordTree = phraseChunker.parse(posTaggedWords)
    print("POS Tagged and Chunked Sentence as Word Tree:")
    print(wordTree)
    print("")
        
    #find sentences that fit a simple pattern: NP /  VP / NP /  , or CC / NP / , or CC (and so on)
    # can strip away additional NP: NP / NP / VP ...
    isSentenceInAcceptableFormat = True #this should check against simple pattern for now. eventually this will be a complex REGEX check
    isLookingForFirstNounPhrase = True
    isLookingForFirstVerbPhrase = False
    isLookingForNounPhrasesAfterVerb = False
    
    print("Noun and Verb Phrases to be used in questions and answers:")
    subjectNoun = ""
    verb = ""
    objectNouns = []
    # for "ands" and commas, create new sentence of format NP VP NP, making list of simple sentences from a compound sentence
    for subtree in wordTree.subtrees():
        if subtree.label() == 'NP':
            if isLookingForFirstNounPhrase:
                subjectNoun = subtree
                subjectNoun = ' '.join(word for word, tag in subjectNoun.leaves())
                print(subjectNoun)
                isLookingForFirstNounPhrase = False
                isLookingForFirstVerbPhrase = True
            if isLookingForNounPhrasesAfterVerb:
                objectNoun = subtree
                objectNoun = ' '.join(word for word, tag in objectNoun.leaves())
                print(objectNoun)
                objectNouns.append(objectNoun)
        if subtree.label() == 'VP':
            if isLookingForFirstVerbPhrase:
                verb = subtree
                verb = ' '.join(word for word, tag in verb.leaves())
                print(verb)
                isLookingForFirstVerbPhrase = False
                isLookingForNounPhrasesAfterVerb = True
            else:
                isSentenceInAcceptableFormat = False
    
    print("")
    print("Sentence Suitability:")
    if isSentenceInAcceptableFormat == False:
        print("Sentence may not be suitable for questions.")
        print("")
    else:
        print("Sentence appears to fit question creation format.")
        print("")
    #question and answer formatter: crude
    # no question word determiner, just "What [VP] [NP] ? Answer: [Other NP]" 
    # do this two ways for each simple sentence: first NP and second NP as question and answer then switch
    quizQuestions = []
    #Correct question word based on first entity identifier for NP. If none, stick with What. Will learn how well this simple rule holds.
    subtreeLabel = ""
    for subtree in namedEntities.subtrees():
        if subtreeLabel == "" or subtreeLabel == "S": #"S" is commonly first subtree when sentence is flagged as label
            subtreeLabel = subtree.label()
    questionWord =  getQuestionWord(subtreeLabel)
    print("entity type for determining question word: " + subtreeLabel)
    print("Question Word: " + questionWord)
    print("")
    print("Generated Questions and Answers:")
    #objects as answers
    for objectNoun in objectNouns:
        quizQuestion = "Question: " + questionWord + ' ' + verb + ' ' + subjectNoun + "? Answer: " + objectNoun
        quizQuestions.append(quizQuestion)
    #subject as answers
    for objectNoun in objectNouns:
        quizQuestion = "Question: " + questionWord + ' ' + verb + ' ' + objectNoun + "? Answer: " + subjectNoun
        quizQuestions.append(quizQuestion)
    #print results
    for quizQuestion in quizQuestions:
        print(quizQuestion)
