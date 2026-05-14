<<<<<<< HEAD
from sklearn.tree import DecisionTreeClassifier

def train_dt(X, y):
    model = DecisionTreeClassifier(criterion="entropy")
    model.fit(X, y)
=======
from sklearn.tree import DecisionTreeClassifier

def train_dt(X, y):
    model = DecisionTreeClassifier(criterion="entropy")
    model.fit(X, y)
>>>>>>> 07cb0cbfc6be93d9be7f2b736ba6a03aa51ca954
    return model