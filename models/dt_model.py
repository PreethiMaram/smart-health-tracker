from sklearn.tree import DecisionTreeClassifier

def train_dt(X, y):
    model = DecisionTreeClassifier(criterion="entropy")
    model.fit(X, y)
    return model