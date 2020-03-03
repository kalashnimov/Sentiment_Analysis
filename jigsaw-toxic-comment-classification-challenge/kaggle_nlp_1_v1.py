# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 15:03:22 2019

@author: Jie.Hu
"""

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score
from scipy.sparse import hstack

class_names = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

train = pd.read_csv('C:/Users/Jie.Hu/Desktop/Data Science/Practice/Kaggle_nlp_1/train.csv').fillna(' ')
test = pd.read_csv('C:/Users/Jie.Hu/Desktop/Data Science/Practice/Kaggle_nlp_1/test.csv').fillna(' ')

train_text = train['comment_text']
test_text = test['comment_text']
all_text = pd.concat([train_text, test_text])

word_vectorizer = TfidfVectorizer(
    sublinear_tf=True,
    strip_accents='unicode',
    analyzer='word',
    #token_pattern=r'\w{1,}',
    stop_words='english',
    ngram_range=(1, 2))
word_vectorizer.fit(all_text)
train_word_features = word_vectorizer.transform(train_text)
test_word_features = word_vectorizer.transform(test_text)

char_vectorizer = TfidfVectorizer(
    sublinear_tf=True,
    strip_accents='unicode',
    analyzer='char',
    stop_words='english',
    ngram_range=(2, 4))
char_vectorizer.fit(all_text)
train_char_features = char_vectorizer.transform(train_text)
test_char_features = char_vectorizer.transform(test_text)

train_features = hstack([train_char_features, train_word_features])
test_features = hstack([test_char_features, test_word_features])

# keep the top 10% features
from sklearn.feature_selection import SelectPercentile, f_classif
selector = SelectPercentile(f_classif, 10)
selector.fit(train_features, train['toxic'].values)
train_features_trans = selector.transform(train_features)
test_features_trans = selector.transform(test_features)


# logistic regression
scores = []
#submission = pd.DataFrame.from_dict({'id': test['id']})
for class_name in class_names:
    train_target = train[class_name]
    classifier = LogisticRegression(C=0.9, solver='saga', max_iter=1000)

    cv_score = np.mean(cross_val_score(classifier, train_features, train_target, cv=3, scoring='roc_auc'))
    scores.append(cv_score)
    print('CV score for class {} is {}'.format(class_name, cv_score))

    #classifier.fit(train_features, train_target)
    #submission[class_name] = classifier.predict_proba(test_features)[:, 1]

print('Total CV score is {}'.format(np.mean(scores)))

#submission.to_csv('submission.csv', index=False)
 
    
# find optimal c by cv
scores = []
c_values = [0.9,1]
for class_name in class_names:
    for c in c_values:
        train_target = train[class_name]
        clf = LogisticRegression(C=c, solver='saga', max_iter=10000)

        cv_score = np.mean(cross_val_score(clf, train_features, train_target, cv=3, scoring='roc_auc'))
        scores.append([class_name, c, cv_score])
        print('cv score for class {} with regularization {} is {:0.5f}'.format(class_name, c, cv_score))


#custom NBSVM model
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_is_fitted
from sklearn.linear_model import LogisticRegression
from scipy import sparse

class NbSvmClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, C=1.0, dual=False):
        self.C = C
        self.dual = dual

    def predict(self, x):
        # Verify that model has been fit
        check_is_fitted(self, ['_r', '_clf'])
        return self._clf.predict(x.multiply(self._r))

    def predict_proba(self, x):
        # Verify that model has been fit
        check_is_fitted(self, ['_r', '_clf'])
        return self._clf.predict_proba(x.multiply(self._r))

    def fit(self, x, y):
        # Check that X and y have correct shape
        y = y.values
        x, y = check_X_y(x, y, accept_sparse=True)

        def pr(x, y_i, y):
            p = x[y==y_i].sum(0)
            return (p+1) / ((y==y_i).sum()+1)

        self._r = sparse.csr_matrix(np.log(pr(x,1,y) / pr(x,0,y)))
        x_nb = x.multiply(self._r)
        self._clf = LogisticRegression(C=self.C, dual=self.dual).fit(x_nb, y)
        return self
    
scores = []
for class_name in class_names:
    train_target = train[class_name]
    clf = NbSvmClassifier(C=3, dual=True)
    
    cv_score = np.mean(cross_val_score(clf, train_features, train_target, cv=3, scoring='roc_auc'))
    scores.append(cv_score)
    print('cv score for class {} is {:0.5f}'.format(class_name, cv_score))
    
print('Total CV score is {:0.5f}'.format(np.mean(scores)))    

# find optimal c by cv
scores = []
c_values = [2,3,4]
for class_name in class_names:
    for c in c_values:
        train_target = train[class_name]
        clf = NbSvmClassifier(C=c, dual=True)

        cv_score = np.mean(cross_val_score(clf, train_features_trans, train_target, cv=3, scoring='roc_auc'))
        scores.append([class_name, c, cv_score])
        print('cv score for class {} with regularization {} is {:0.5f}'.format(class_name, c, cv_score))


# submission
submission = pd.DataFrame.from_dict({'id': test['id']})
for class_name in class_names:
    train_target = train[class_name]
    clf = LogisticRegression(C=0.9, solver='saga', max_iter=1000)
    #clf = NbSvmClassifier(C=3, dual=True)
    clf.fit(train_features, train_target)
    submission[class_name] = clf.predict_proba(test_features)[:, 1]
submission.to_csv("submission2.csv", index = False)    


scores = []
submission = pd.DataFrame.from_dict({'id': test['id']})
for class_name in class_names:
    train_target = train[class_name]
    clf = NbSvmClassifier(C=2, dual=True)

    cv_score = np.mean(cross_val_score(clf, train_features_trans, train_target, cv=3, scoring='roc_auc'))
    scores.append(cv_score)
    print('CV score for class {} is {}'.format(class_name, cv_score))

    clf.fit(train_features_trans, train_target)
    submission[class_name] = clf.predict_proba(test_features_trans)[:, 1]

print('Total CV score is {}'.format(np.mean(scores)))
submission.to_csv('submission3.csv', index=False)


scores = []
submission = pd.DataFrame.from_dict({'id': test['id']})
for class_name in class_names:
    train_target = train[class_name]
    clf = NbSvmClassifier(C=3, dual=True)

    #cv_score = np.mean(cross_val_score(clf, train_features, train_target, cv=3, scoring='roc_auc'))
    #scores.append(cv_score)
    #print('CV score for class {} is {}'.format(class_name, cv_score))

    clf.fit(train_features, train_target)
    submission[class_name] = clf.predict_proba(test_features)[:, 1]

#print('Total CV score is {}'.format(np.mean(scores)))
submission.to_csv('submission4.csv', index=False)


x = train_features
test_x = test_features

def pr(y_i, y):
    p = x[y==y_i].sum(0)
    return (p+1) / ((y==y_i).sum()+1)

def get_mdl(y):
    y = y.values
    r = np.log(pr(1,y) / pr(0,y))
    m = LogisticRegression(C=3, dual=True)
    x_nb = x.multiply(r)
    return m.fit(x_nb, y), r

preds = np.zeros((len(test), len(class_names)))

for i, j in enumerate(class_names):
    print('fit', j)
    m,r = get_mdl(train[j])
    preds[:,i] = m.predict_proba(test_x.multiply(r))[:,1]