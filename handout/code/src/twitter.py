"""
Author      : Yi-Chieh Wu, Sriram Sankararman
Description : Twitter
"""

from string import punctuation

import numpy as np
from sklearn.model_selection import train_test_split

# !!! MAKE SURE TO USE SVC.decision_function(X), NOT SVC.predict(X) !!!
# (this makes ``continuous-valued'' predictions)
from sklearn.svm import SVC
from sklearn.cross_validation import StratifiedKFold
from sklearn import metrics

######################################################################
# functions -- input/output
######################################################################

def read_vector_file(fname):
    """
    Reads and returns a vector from a file.
    
    Parameters
    --------------------
        fname  -- string, filename
        
    Returns
    --------------------
        labels -- numpy array of shape (n,)
                    n is the number of non-blank lines in the text file
    """
    return np.genfromtxt(fname)


######################################################################
# functions -- feature extraction
######################################################################

def extract_words(input_string):
    """
    Processes the input_string, separating it into "words" based on the presence
    of spaces, and separating punctuation marks into their own words.
    
    Parameters
    --------------------
        input_string -- string of characters
    
    Returns
    --------------------
        words        -- list of lowercase "words"
    """
    
    for c in punctuation :
        input_string = input_string.replace(c, ' ' + c + ' ')
    return input_string.lower().split()


def extract_dictionary(infile):
    """
    Given a filename, reads the text file and builds a dictionary of unique
    words/punctuations.
    
    Parameters
    --------------------
        infile    -- string, filename
    
    Returns
    --------------------
        word_list -- dictionary, (key, value) pairs are (word, index)
    """
    
    word_list = {}
    index = 0
    with open(infile, 'rU') as fid :
        # for each line in the text file
        for line in fid:
            # get list of words from line
            extracted_words = extract_words(line)
            for word in extracted_words:
                if word not in word_list:
                    word_list[word] = index
                    index += 1
            
        ### ========== TODO : START ========== ###
        # part 1a: process each line to populate word_list
        ### ========== TODO : END ========== ###

    return word_list


def extract_feature_vectors(infile, word_list):
    """
    Produces a bag-of-words representation of a text file specified by the
    filename infile based on the dictionary word_list.
    
    Parameters
    --------------------
        infile         -- string, filename
        word_list      -- dictionary, (key, value) pairs are (word, index)
    
    Returns
    --------------------
        feature_matrix -- numpy array of shape (n,d)
                          boolean (0,1) array indicating word presence in a string
                            n is the number of non-blank lines in the text file
                            d is the number of unique words in the text file
    """
    
    num_lines = sum(1 for line in open(infile,'rU'))
    num_words = len(word_list)
    feature_matrix = np.zeros((num_lines, num_words))
    
    with open(infile, 'rU') as fid :
        ### ========== TODO : START ========== ###
        # part 1b: process each line to populate feature_matrix
        for num, line in enumerate(fid, 0):
            # extract words from line in tweet file
            extracted_words = extract_words(line)

            # populate feature in each row
            for word in extracted_words:
                feature_matrix[num][word_list[word]] = 1

        ### ========== TODO : END ========== ###
        
    return feature_matrix


######################################################################
# functions -- evaluation
######################################################################

def performance(y_true, y_pred, metric="accuracy"):
    """
    Calculates the performance metric based on the agreement between the 
    true labels and the predicted labels.
    
    Parameters
    --------------------
        y_true -- numpy array of shape (n,), known labels
        y_pred -- numpy array of shape (n,), (continuous-valued) predictions
        metric -- string, option used to select the performance measure
                  options: 'accuracy', 'f1-score', 'auroc'       
    
    Returns
    --------------------
        score  -- float, performance score
    """
    # map continuous-valued predictions to binary labels
    y_label = np.sign(y_pred)
    y_label[y_label==0] = 1
    
    ### ========== TODO : START ========== ###
    # part 2a: compute classifier performance

    # if metric chosen is accuracy
    if metric == "accuracy":
        return metrics.accuracy_score(y_true, y_label)
    
    elif metric == "f1_score":
        return metrics.f1_score(y_true, y_label)
    
    elif metric == "auroc":
        return metrics.roc_auc_score(y_true, y_pred)
    else:
        return -1

    ### ========== TODO : END ========== ###


def cv_performance(clf, X, y, kf, metric="accuracy"):
    """
    Splits the data, X and y, into k-folds and runs k-fold cross-validation.
    Trains classifier on k-1 folds and tests on the remaining fold.
    Calculates the k-fold cross-validation performance metric for classifier
    by averaging the performance across folds.
    
    Parameters
    --------------------
        clf    -- classifier (instance of SVC)
        X      -- numpy array of shape (n,d), feature vectors
                    n = number of examples
                    d = number of features
        y      -- numpy array of shape (n,), binary labels {1,-1}
        kf     -- cross_validation.KFold or cross_validation.StratifiedKFold
        metric -- string, option used to select performance measure
    
    Returns
    --------------------
        score   -- float, average cross-validation performance across k folds
    """

    ### ========== TODO : START ========== ###
    # part 2b: compute average cross-validation performance    
    accuracy_list = []

    for train, test in kf:
        
        clf.fit(X[train], y[train])
        predictions = clf.decision_function(X[test])
        accuracy_list.append(performance(y[test], predictions, metric))

    return sum(accuracy_list)/float(len(accuracy_list))

    ### ========== TODO : END ========== ###


def select_param_linear(X, y, kf, metric="accuracy"):
    """
    Sweeps different settings for the hyperparameter of a linear-kernel SVM,
    calculating the k-fold CV performance for each setting, then selecting the
    hyperparameter that 'maximize' the average k-fold CV performance.
    
    Parameters
    --------------------
        X      -- numpy array of shape (n,d), feature vectors
                    n = number of examples
                    d = number of features
        y      -- numpy array of shape (n,), binary labels {1,-1}
        kf     -- cross_validation.KFold or cross_validation.StratifiedKFold
        metric -- string, option used to select performance measure
    
    Returns
    --------------------
        C -- float, optimal parameter value for linear-kernel SVM
    """
    
    print 'Linear SVM Hyperparameter Selection based on ' + str(metric) + ':'
    C_range = 10.0 ** np.arange(-3, 3)
    max_score = -1
    best_c = -1

    for c in range(0, len(C_range)):
        clf = SVC(kernel='linear', C=C_range[c])
        print ('%.4f' % C_range[c])
        cur_perf = cv_performance(clf, X, y, kf, metric)
        print ('%.4f' % cur_perf)
        if cur_perf >= max_score:
            max_score = cur_perf
            best_c = C_range[c]
    
    print best_c

    ### ========== TODO : START ========== ###
    # part 2: select optimal hyperparameter using cross-validation
    return best_c
    ### ========== TODO : END ========== ###



def performance_test(clf, X, y, metric="accuracy"):
    """
    Estimates the performance of the classifier using the 95% CI.
    
    Parameters
    --------------------
        clf          -- classifier (instance of SVC)
                          [already fit to data]
        X            -- numpy array of shape (n,d), feature vectors of test set
                          n = number of examples
                          d = number of features
        y            -- numpy array of shape (n,), binary labels {1,-1} of test set
        metric       -- string, option used to select performance measure
    
    Returns
    --------------------
        score        -- float, classifier performance
    """

    ### ========== TODO : START ========== ###
    # part 3: return performance on test data by first computing predictions and then calling performance

    predictions = clf.decision_function(X)
    return performance(y, predictions, metric)
    ### ========== TODO : END ========== ###


######################################################################
# main
######################################################################
 
def main() :
    np.random.seed(1234)
    
    # read the tweets and its labels   
    dictionary = extract_dictionary('../data/tweets.txt')

    # print dictionary

    X = extract_feature_vectors('../data/tweets.txt', dictionary)

    y = read_vector_file('../data/labels.txt')
    
    metric_list = ["accuracy", "f1_score", "auroc"]
    
    # Get shape of feature matrix
    n, d = X.shape
    print ('Feature matrix is a %dx%d matrix' % (n, d))


    ### ========== TODO : START ========== ###
    # part 1: split data into training (training + cross-validation) and testing set
    
    # split data into train and test sets 
    # make sure shuffle is false  

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size = float(560)/630, shuffle = False)

    # part 2: create stratified folds (5-fold CV)
    
    kf = StratifiedKFold(y_train, 5)

    # part 2: for each metric, select optimal hyperparameter for linear-kernel SVM using CV

    print ('accuracy metric: %d' % (select_param_linear(X_train, y_train, kf, metric_list[0])))
    print ('f1_score metric: %d' % (select_param_linear(X_train, y_train, kf, metric_list[1])))
    print ('auroc metric: %d' % (select_param_linear(X_train, y_train, kf, metric_list[2])))


    # part 3: train linear-kernel SVMs with selected hyperparameters
    
    clf = SVC(C = 100.0, kernel='linear')
    clf.fit(X_train, y_train)

    print ('accuracy metric: %.4f' % (performance_test(clf, X_test, y_test, metric_list[0])))
    print ('f1_score metric: %.4f' % (performance_test(clf, X_test, y_test, metric_list[1])))
    print ('auroc metric: %.4f' % (performance_test(clf, X_test, y_test, metric_list[2])))


    # part 3: report performance on test data
    
    ### ========== TODO : END ========== ###
    
    
if __name__ == "__main__" :
    main()
