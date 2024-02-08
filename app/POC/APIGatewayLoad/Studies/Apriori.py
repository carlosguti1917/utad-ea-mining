# source https://hands-on.cloud/implementation-of-apriori-algorithm-using-python/#h-using-apriori-algorithm-in-python
# importing module
import pandas as pd
import numpy as np
# importing required module
import plotly.express as px

# dataset
data = pd.read_csv("C:/Temp/Utad/Apriori/Market_Basket_Optimisation.csv")

# printing the shape of the dataset
print(data.shape)
# printing the heading
print("printing the heading")
print(data.head())

#Let’s print out the top 10 most frequent items from the dataset.
# Gather All Items of Each Transactions into Numpy Array
transaction = []
print("entra")
for i in range(0, data.shape[0]):
    for j in range(0, data.shape[1]):
        transaction.append(data.values[i, j])
# converting to numpy array
print("sai")
transaction = np.array(transaction)
#  Transform Them a Pandas DataFrame
df = pd.DataFrame(transaction, columns=["items"])
# Put 1 to Each Item For Making Countable Table, to be able to perform Group By
df["incident_count"] = 1
#  Delete NaN Items from Dataset
indexNames = df[df['items'] == "nan" ].index
df.drop(indexNames , inplace=True)
# Making a New Appropriate Pandas DataFrame for Visualizations
df_table = df.groupby("items").sum().sort_values("incident_count", ascending=False).reset_index()
#  Initial Visualizations
df_table.head(10).style.background_gradient(cmap='Greens')

# to have a same origin
df_table["all"] = "all"

# creating tree map using plotly
fig = px.treemap(df_table.head(30), path=['all', "items"], values='incident_count',
                  color=df_table["incident_count"].head(30), hover_data=['items'],
                  color_continuous_scale='Greens',
                )
# ploting the treemap
#fig.show()

#Encoding the dataset
#Before getting the most frequent itemsets, we need to transform our dataset into a True – False matrix
# importing the required module
from mlxtend.preprocessing import TransactionEncoder

# initializing the transactionEncoder
te = TransactionEncoder()
te_ary = te.fit(transaction).transform(transaction)
dataset = pd.DataFrame(te_ary, columns=te.columns_)

# dataset after encoded
print(dataset)

# select top 50 items
first50 = df_table["items"].head(50).values
# Extract Top50
dataset = dataset.loc[:, first50]
# shape of the dataset
print(dataset.shape)

# importing the required module
from mlxtend.frequent_patterns import apriori, association_rules


# Extracting the most frequest itemsets via Mlxtend.
# The length column has been added to increase ease of filtering.
frequent_itemsets = apriori(dataset, min_support=0.01, use_colnames=True)
frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))

# printing the frequent itemset
print(frequent_itemsets)

# printing the frequntly items
#print out all items with a length of 2, and the minimum support is more than 0.05.
frequent_itemsets[(frequent_itemsets['length'] == 2) & (frequent_itemsets['support'] >= 0.05)]
print(frequent_itemsets)

# printing the frequntly items with length 3
frequent_itemsets[(frequent_itemsets['length'] == 3)].head(3)
print(frequent_itemsets)

#let’s create antecedents and consequents:
#  We set our metric as "Lift" to define whether antecedents & consequents are dependent our not
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.2)
rules["antecedents_length"] = rules["antecedents"].apply(lambda x: len(x))
rules["consequents_length"] = rules["consequents"].apply(lambda x: len(x))
rules.sort_values("lift",ascending=False)

#Confidence
# Sort values based on confidence
rules.sort_values("confidence",ascending=False)