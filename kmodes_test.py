import numpy as np
from kmodes import kmodes

# random categorical data
data = np.random.choice(20, (100, 10))

km = kmodes.KModes(n_clusters=4, init='Huang', n_init=5, verbose=1)

clusters = km.fit_predict(data)

# Print the cluster centroids
print(km.cluster_centroids_)
