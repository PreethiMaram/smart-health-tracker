<<<<<<< HEAD
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

def train_knn(X, y):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    k = min(5, len(X))
    if k == 0:
        k = 1

    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_scaled, y)

=======
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

def train_knn(X, y):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    k = min(5, len(X))
    if k == 0:
        k = 1

    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_scaled, y)

>>>>>>> 07cb0cbfc6be93d9be7f2b736ba6a03aa51ca954
    return model, scaler