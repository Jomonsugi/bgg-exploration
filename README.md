# Board Game Geek Recommender 

### Goal

Build a collaborative recommendation system for current users of boardgamegeek.com, further filtering the results by categories gained from the game descriptions using natural language processing, board game statistics, and user input.

### Data collection
boardgamegeek.com has an API that allowed me to access XML output for each board game and each user. I used web-scraping techniques to fill obtain unique ids for every game in the database and from there wrote scripts to call the API, assign variables from a json output, and organize all records in a MongoDB database. I found that there is a 5 second rule on API calls, which meant I had to run my script for a few days. As a result I ran the script on an AWS instance, moved the MongoDB data to EC2, and then pulled the data down locally from there. I made a preliminary cutoff at 1000 games.

### Dataset
When putting my data into MongoDB, I organized my data into two datasets:
- Comments/ratings: this included every rating and comment made by users on the first 1000 board games (1.3 million records, 65,000 unique users)

- Statistics: (note "statistics" is the name boardgamegeek.com gives this group when calling the API so I am following suit) In total 161 columns, 131 of which were boolean values indicating whether a game belonged to a particular mechanic or category group. I included the board game description as a variables here as well. Other highlighted variables were board game weight (complexity), play time, best number of players, and various user voted ratings.

### Clustering and Distance Matrices
Most of my EDA concerned the second dataset of statistics as I wanted to find variables that could be possibly be clustered together or otherwise give a strong indication of a game someone might like with strong preferences. I used k-modes and k-prototype on various variables and through silhouette scores/plots found promising groups in the mechanic and category groups. I then created hammond distance matrices as a tool to find the most similar games to any particular game based on it's combinations of mechanics and categories. From domain knowledge, I want to note that I believe these distance matrices alone would be a powerful way to suggest a game to someone. Results could be further filtered by the complexity of the game, and user input like number of players and time.  For this project I decided to move forward and pursue other techniques, but I would like to come back to this intuition in the future to further develop the idea.

### Natural Language Processing
From my project goals, I used NLP techniques to find explore possible clusters within the description and user comments. I used a combination of spaCy, Sk-learn, and NLTK to preprocess the data. I filtered out HTML content, removed conventional stop words (and later custom stop words that I found to be domain specific), tokenized, lemmatized, and then transformed all documents to a Tf-idf matrix. From there I started with LDA to look at possible clusters among board game descriptions, using a package called ldaviz to explore my output. Through many iterations I found LDA grouped a large metatopic that I could just call "board gaming" and smaller topics that overlapped each other. Instead of trusting the output I moved to non-negative matrix factorization and immediately found good results. NMF, grouped the game descriptions into intuitive and helpful thematic groups. Further goals are to use NMF to group the comments, as I found similar results to descriptions using LDA.

### Spark and Alternating Least Squares
After find a few promising ideas/results from exploring the statistics data set I moved on to the comments/ratings. My dataset lended to leveraging Spark's machine learning library as the dataset was quite large and I only pulled ratings/comments down for the first 1000 games so I wanted to create a scalable system for future growth. I started by pulling the data from MongoDB directly into a Spark's data structures (RDD and DataFrame). From there I further organized the data, trained/tested an ALS model, created a dataframe of users and games they have not rated and used my optimized model to create a new dataframe with predictions.

### Current Work
At this point I have a scalable workflow where I have automated scripts to put data into mongodb, pull the data into Spark, optimize my model with any new data, and produce predictions for all users. From here I want to put the predictions into a pandas DataFrame and circle back to my statitics data features. Although the results I have are enough to make a strong recommendation for a user, I would like to use domain knowledge to further curate the list. Distributing recommendations by the topics I produced using NMF, game complexity, mechanics, and categories, along with user input all come to mind.

### Flask APP
My tool lends itself to an app. Currently, I am working on producing a simple, one page app using Flask that allows the user to input their unique user name from boardgamegeek.com and produce a list of recommendations.

#### Site:

https://boardgamegeek.com/browse/boardgame

#### References

http://www.cs.columbia.edu/~blei/papers/WangBlei2011.pdf

https://satwikkottur.github.io/reports/F14-ML-Report.pdf

http://infolab.stanford.edu/~ullman/mmds/ch9.pdf


#### Code

https://github.com/blei-lab/ctr

https://github.com/d4le/recommend

https://github.com/samweaver/mongodb-spark/blob/master/movie-recommendations/src/main/python/movie-recommendations.py
