---
imported_hash: 8f2a71e0c2823f24
title: Word Cloud on PetFinder datasets
summary: The PetFinder dataset consists of cats/dogs information posted for adoption.
order: 24
kind: notebook
section: Word cloud
source: learn-ai-engineering/data-science/intro-to-nlp/word-cloud/world-cloud-pet-finder.ipynb
---

# Word Cloud on PetFinder datasets


The PetFinder dataset consists of cats/dogs information posted for adoption.

**Word Cloud** is a visual representation object for text processing that shows most frequent words with a bigger and bolder font with different colors. Smaller size words indicate that they are less important.

**Processing Steps**
- Import train and test datasets
- Merge them into a new dataset
- Explore the Pet Type data
- Apply wordcloud to Pet names and explore it
- Check out the breed and breed subtype data
- Use wordcloud on the description column

## Data Fields
- PetID - Unique hash ID of pet profile
- AdoptionSpeed - Categorical speed of adoption. Lower is faster. This is the value to predict. See below section for more info.
- Type - Type of animal (1 = Dog, 2 = Cat)
- Name - Name of pet (Empty if not named)
- Age - Age of pet when listed, in months
- Breed1 - Primary breed of pet (Refer to BreedLabels dictionary)
- Breed2 - Secondary breed of pet, if pet is of mixed breed (Refer to BreedLabels dictionary)
- Gender - Gender of pet (1 = Male, 2 = Female, 3 = Mixed, if profile represents group of pets)
- Color1 - Color 1 of pet (Refer to ColorLabels dictionary)
- Color2 - Color 2 of pet (Refer to ColorLabels dictionary)
- Color3 - Color 3 of pet (Refer to ColorLabels dictionary)
- MaturitySize - Size at maturity (1 = Small, 2 = Medium, 3 = Large, 4 = Extra Large, 0 = Not Specified)
- FurLength - Fur length (1 = Short, 2 = Medium, 3 = Long, 0 = Not Specified)
- Vaccinated - Pet has been vaccinated (1 = Yes, 2 = No, 3 = Not Sure)
- Dewormed - Pet has been dewormed (1 = Yes, 2 = No, 3 = Not Sure)
- Sterilized - Pet has been spayed / neutered (1 = Yes, 2 = No, 3 = Not Sure)
- Health - Health Condition (1 = Healthy, 2 = Minor Injury, 3 = Serious Injury, 0 = Not Specified)
- Quantity - Number of pets represented in profile
- Fee - Adoption fee (0 = Free)
- State - State location in Malaysia (Refer to StateLabels dictionary)
- RescuerID - Unique hash ID of rescuer
- VideoAmt - Total uploaded videos for this pet
- PhotoAmt - Total uploaded photos for this pet
- Description - Profile write-up for this pet. The primary language used is English, with some in Malay or Chinese.

## AdoptionSpeed

### Values indicate following:
0 - Pet was adopted on the same day as it was listed.<br>
1 - Pet was adopted between 1 and 7 days (1st week) after being listed.<br>
2 - Pet was adopted between 8 and 30 days (1st month) after being listed.<br>
3 - Pet was adopted between 31 and 90 days (2nd & 3rd month) after being listed.<br>
4 - No adoption after 100 days of being listed. (There are no pets in this dataset that waited between 90 and 100 days).<br>

```python
# importing packages
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

from wordcloud import WordCloud
from PIL import Image

%matplotlib inline
# plt.style.use('ggplot')
warnings.filterwarnings('ignore')
pd.set_option("display.max_columns", None)
```

## Data Processing

```python
# reading the training dataset
train = pd.read_csv('./data/pet-train.csv', encoding = 'utf-8')
```

```python
# checking shape
train.shape
```

```python
# reading the test dataset
test = pd.read_csv('./data/pet-test.csv', encoding = 'utf-8')
```

```python
# checking shape
test.shape
```

```python
# adding a column called dataset and set all its value to train
train['dataset'] = 'train'
```

```python
# adding a column called dataset and set all values to test
test['dataset'] = 'test'
```

```python
# creating a new df by merging the test dataset into train
merged = train.append(test, ignore_index = True)
```

```python
# checking shape of the merged df
merged.shape
```

```python
# checking frist rows
merged.head(2)
```

```python
# checking last few rows
merged.tail(2)
```

```python
# checking info of the df
merged.info()
```

```python
# transposing df
merged.describe().transpose()
```

```python
# describing df
merged.describe(include = 'object').transpose()
```

## Utility Functions

```python
# creating functions to plot data
main_count = train['AdoptionSpeed'].value_counts(normalize=True).sort_index()
def prepare_plot_dict(df, col, main_count):
    """
    Preparing dictionary with data for plotting to show how much higher/lower are the rates
    of 'Adoption Speed' for the current column comparing to base values (as described higher).
    At first, calculate base rates, then for each category in the column, calculate rates of
    'Adoption Speed' and find difference with the base rates.

    """
    main_count = dict(main_count)
    plot_dict = {}
    for i in df[col].unique():
        val_count = dict(df.loc[df[col] == i, 'AdoptionSpeed'].value_counts().sort_index())

        for k, v in main_count.items():
            if k in val_count:
                plot_dict[val_count[k]] = ((val_count[k] / sum(val_count.values())) / main_count[k]) * 100 - 100
            else:
                plot_dict[0] = 0

    return plot_dict

def make_count_plot(df, x, hue='AdoptionSpeed', title='', main_count=main_count):
    """
    Plotting countplot with correct annotations.
    """
    g = sns.countplot(x=x, data=df, hue=hue);
    plt.title(f'AdoptionSpeed {title}');
    ax = g.axes

    plot_dict = prepare_plot_dict(df, x, main_count)

    for p in ax.patches:
        h = p.get_height() if str(p.get_height()) != 'nan' else 0
        text = f"{plot_dict[h]:.0f}%" if plot_dict[h] < 0 else f"+{plot_dict[h]:.0f}%"
        ax.annotate(text, (p.get_x() + p.get_width() / 2., h),
             ha='center', va='center', fontsize=11, color='green' if plot_dict[h] > 0 else 'red',
                    rotation=0, xytext=(0, 10),
             textcoords='offset points')


def plot_four_graphs(col='', main_title='', dataset_title=''):
    """
    Plotting four graphs:
    - adoption speed by variable;
    - counts of categories in the variable in train and test;
    - adoption speed by variable for dogs;
    - adoption speed by variable for cats;
    """
    plt.figure(figsize=(20, 12));
    plt.subplot(2, 2, 1)
    make_count_plot(df=train, x=col, title=f'and {main_title}')

    plt.subplot(2, 2, 2)
    sns.countplot(x='dataset', data=merged, hue=col);
    plt.title(dataset_title);

    plt.subplot(2, 2, 3)
    make_count_plot(df=train.loc[train['Type'] == 1], x=col, title=f'and {main_title} for dogs')

    plt.subplot(2, 2, 4)
    make_count_plot(df=train.loc[train['Type'] == 2], x=col, title=f'and {main_title} for cats')
```

## Adoption Speed Exploration

```python
# plotting the 'Adoption Speed' for the overall dataset
merged['AdoptionSpeed'].value_counts().sort_index().plot(kind = 'barh', color='steelblue')
plt.xlabel('count')
plt.ylabel('days')
plt.title('Adoption speed classes counts')
plt.show()
```

```python
# plotting the 'Adoption Speed' from the training dataset
plt.figure(figsize=(14, 6));
g = sns.countplot(x='AdoptionSpeed', data=merged.loc[merged['dataset'] == 'train']);
plt.title('Adoption speed classes rates');
ax=g.axes
```

```python
# plotting the same informaion as above - add percentages for each class
plt.figure(figsize=(14, 8));
g = sns.countplot(x='AdoptionSpeed', data=merged.loc[merged['dataset'] == 'train'])
plt.title('Adoption speed classes rates');
ax=g.axes
for p in ax.patches:
     ax.annotate(f"{p.get_height() * 100 / train.shape[0]:.2f}%", (p.get_x() + p.get_width() / 2., p.get_height()),
         ha='center', va='center', fontsize=11, color='gray', rotation=0, xytext=(0, 10),
         textcoords='offset points')
```

We can see that some pets were adopted immediately, but these are rare cases: maybe someone wanted to adopt any pet, or the pet was lucky to be seen by person, who wanted a similar pet.

It is nice that a lot of pets are adopted within a first week of being listed!

One more interesting thing is that the classes have a linear relationship - the higher the number, the worse situation is. So it could be possible to build not only multiclass classification, but also regression.

## Pet Type
1 is Dog, 2 is Cat

```python
# getting values count
merged['Type'].value_counts()
```

```python
# converting the pet type
merged['Type'] = merged['Type'].apply(lambda x: 'Dog' if x == 1 else 'Cat')
merged['Type'].value_counts()
```

```python
# plotting 'Type' col for both dfs
plt.figure(figsize=(10, 8));
sns.countplot(x='dataset', data = merged, hue = 'Type');
plt.title('Number of cats and dogs in train and test data');
```

```python
# plotting 'Adoptoon Speed' / pet type
plt.figure(figsize=(18, 8));
make_count_plot(df=merged.loc[merged['dataset'] == 'train'], x='Type', title='by pet Type')
```

We can see that cats are more likely to be adopted early than dogs and overall the percentage of not adopted cats is lower. Does this mean people prefer cats? Or maybe this dataset is small and could contain bias. On the other hand more dogs are adopted after several months.

## Pet Name

**Are names important in adoption?**

At first let's look at most common names using wordcloud

```python
# plotting top names
fig, ax = plt.subplots(figsize = (16, 12))
# nrows, ncols, index - index 1 means upper left corner and increases to right
plt.subplot(1, 2, 1)
text_cat = ' '.join(merged.loc[merged['Type'] == 'Cat', 'Name'].fillna('').values)
wordcloud = WordCloud(max_font_size=None, background_color='white',
                      width=1200, height=1000).generate(text_cat)
plt.imshow(wordcloud)
plt.title('Top Cat Names', fontsize = 30)
plt.axis("off")

#index 2 means second column
plt.subplot(1, 2, 2)
text_dog = ' '.join(merged.loc[merged['Type'] == 'Dog', 'Name'].fillna('').values)
wordcloud = WordCloud(max_font_size=None, background_color='white',
                      width=1200, height=1000).generate(text_dog)
plt.imshow(wordcloud)
plt.title('Top Dog Names', fontsize = 30)
plt.axis("off")

plt.show()
```

It is worth noticing some things:

    - Often we see normal pet names like "Mimi", "Angel" and so on;
    - Quite often people write simply who is there for adoption: "Kitten", "Puppies";
    - Vety often the color of pet is written, sometimes gender;
    - And it seems that sometimes names can be strange or there is some info written instead of the name;

One more thing to notice is that some pets don't have names. Let's see whether this is important

## Most Popular Pet Names and Adoption Speed

```python
# printing the most popular names and Adoption Speed
print('Most Popular Pet Names and AdoptionSpeed')
for n in train['Name'].value_counts().index[:5]:
    print("pet name: {}".format(n))
    print(train.loc[train['Name'] == n, 'AdoptionSpeed'].value_counts().sort_index())
    print('')
```

```python
# replacing null names
train['Name'] = train['Name'].fillna('Unnamed')
test['Name'] = test['Name'].fillna('Unnamed')
merged['Name'] = merged['Name'].fillna('Unnamed')

train['No_name'] = 0
train.loc[train['Name'] == 'Unnamed', 'No_name'] = 1
test['No_name'] = 0
test.loc[test['Name'] == 'Unnamed', 'No_name'] = 1
merged['No_name'] = 0
merged.loc[merged['Name'] == 'Unnamed', 'No_name'] = 1

print(f"Percentage of unnamed Pets in train data: {train['No_name'].sum() * 100 / train['No_name'].shape[0]:.2f}%.")
print(f"Percentage of unnamed Tets in test data:  {test['No_name'].sum() * 100 / test['No_name'].shape[0]:.2f}%.")
```

```python
# plotting Adoption Speed x Having Name
plt.figure(figsize=(18, 8))
make_count_plot(df=merged.loc[merged['dataset'] == 'train'], x='No_name', title='and Having a Name')
```

## Breeds

- There is a main breed of the pet and secondary if relevant
- At first let's see whether having secondary breed influences adoption speed.

```python
# chceking pure breed pets percentage per df
train['Pure_breed'] = 0
train.loc[train['Breed2'] == 0, 'Pure_breed'] = 1
test['Pure_breed'] = 0
test.loc[test['Breed2'] == 0, 'Pure_breed'] = 1
merged['Pure_breed'] = 0
merged.loc[merged['Breed2'] == 0, 'Pure_breed'] = 1

print(f"Rate of pure breed pets in train data: {train['Pure_breed'].sum() * 100 / train['Pure_breed'].shape[0]:.2f}%.")
print(f"Rate of pure breed pets in test data: {test['Pure_breed'].sum() * 100 / test['Pure_breed'].shape[0]:.2f}%.")
```

```python
# plotting number of pets by pure/not-pure breed in train and test data
plot_four_graphs(col='Pure_breed',
                 main_title='having pure breed',
                 dataset_title='Number of pets by pure/not-pure breed in train and test data')
```

It seems that non-pure breed pets tend to be adopted more and faster, especially cats.

```python
# loading the bread type and names
breeds = pd.read_csv('./data/breed_labels.csv', encoding = 'utf-8')
```

```python
# checking frist few rows
breeds.head(2)
```

```python
# creating a dictionary of BreedID and BreedName
breeds_dict = {k: v for k, v in zip(breeds['BreedID'], breeds['BreedName'])}
```

```python
# printing dict
print(breeds_dict)
```

```python
# creating 'Breed' name and the subtype (if no subtype then put '-')
train['Breed1_name'] = train['Breed1'].apply(lambda x: '_'.join(breeds_dict[x].split())
                                             if x in breeds_dict else 'Unknown')
train['Breed2_name'] = train['Breed2'].apply(lambda x: '_'.join(breeds_dict[x])
                                             if x in breeds_dict else '-')
test['Breed1_name'] = test['Breed1'].apply(lambda x: '_'.join(breeds_dict[x].split())
                                           if x in breeds_dict else 'Unknown')
test['Breed2_name'] = test['Breed2'].apply(lambda x: '_'.join(breeds_dict[x].split())
                                           if x in breeds_dict else '-')
merged['Breed1_name'] = merged['Breed1'].apply(lambda x: '_'.join(breeds_dict[x].split())
                                               if x in breeds_dict else 'Unknown')
merged['Breed2_name'] = merged['Breed2'].apply(lambda x: '_'.join(breeds_dict[x].split())
                                               if x in breeds_dict else '-')
```

```python
# defining cols
cols = ['Breed1', 'Breed2', 'Breed1_name', 'Breed2_name', 'Pure_breed']
merged[cols]
```

```python
# appling wordcloud to the columns created above
fig, ax = plt.subplots(figsize = (20, 18))
plt.subplot(2, 2, 1)
text_cat1 = ' '.join(merged.loc[merged['Type'] == 'Cat', 'Breed1_name'].fillna('').values)
wordcloud = WordCloud(max_font_size=None, background_color='white', collocations=False,
                      width=1200, height=1000).generate(text_cat1)
plt.imshow(wordcloud)
plt.title('Top Cat breed1', fontsize = 20)
plt.axis("off")

plt.subplot(2, 2, 2)
text_dog1 = ' '.join(merged.loc[merged['Type'] == 'Dog', 'Breed1_name'].fillna('').values)
wordcloud = WordCloud(max_font_size=None, background_color='white', collocations=False,
                      width=1200, height=1000).generate(text_dog1)
plt.imshow(wordcloud)
plt.title('Top Dog Breed1', fontsize = 20)
plt.axis("off")

plt.subplot(2, 2, 3)
text_cat2 = ' '.join(merged.loc[merged['Type'] == 'Cat', 'Breed2_name'].fillna('').values)
wordcloud = WordCloud(max_font_size=None, background_color='white', collocations=False,
                      width=1200, height=1000).generate(text_cat2)
plt.imshow(wordcloud)
plt.title('Top Cat Breed2', fontsize = 20)
plt.axis("off")

plt.subplot(2, 2, 4)
text_dog2 = ' '.join(merged.loc[merged['Type'] == 'Dog', 'Breed2_name'].fillna('').values)
wordcloud = WordCloud(max_font_size=None, background_color='white', collocations=False,
                      width=1200, height=1000).generate(text_dog2)
plt.imshow(wordcloud)
plt.title('Top Dog breed2', fontsize = 20)
plt.axis("off")
plt.show()
```

It seems that not all values of these features are really breeds.
Sometimes people simply write that the dogs has a mixed breed, cats often are described as domestic with certain hair length.

```python
# checking counts top 15 Breed names
(merged['Breed1_name'] + '__' + merged['Breed2_name']).value_counts().head(15)
```

## Description

Description could have lot of useful information.

```python
# plotting top words in description
fig, ax = plt.subplots(figsize = (12, 8))
text_cat = ' '.join(merged['Description'].fillna('').values)
wordcloud = WordCloud(max_font_size=None, background_color='white',
                      width=1200, height=1000).generate(text_cat)
plt.imshow(wordcloud)
plt.title('Top Words in Description\n', fontsize = 30)
plt.axis("off")
```

```python
# creating new columns - description length and number of words in description
train['Description'] = train['Description'].fillna('')
test['Description'] = test['Description'].fillna('')
merged['Description'] = merged['Description'].fillna('')

train['desc_length'] = train['Description'].apply(lambda x: len(x))
train['desc_words'] = train['Description'].apply(lambda x: len(x.split()))

test['desc_length'] = test['Description'].apply(lambda x: len(x))
test['desc_words'] = test['Description'].apply(lambda x: len(x.split()))

merged['desc_length'] = merged['Description'].apply(lambda x: len(x))
merged['desc_words'] = merged['Description'].apply(lambda x: len(x.split()))

train['average_word_length'] = train['desc_length'] / train['desc_words']
test['average_word_length'] = test['desc_length'] / test['desc_words']
merged['average_word_length'] = merged['desc_length'] / merged['desc_words']
```

```python
# plotting Addoption Speed by type, description len and words
plt.figure(figsize=(16, 6));
plt.subplot(1, 2, 1)
sns.violinplot(x="AdoptionSpeed", y="desc_length", hue="Type", data=train);
plt.title('AdoptionSpeed by Type and Description Length\n');

plt.subplot(1, 2, 2)
sns.violinplot(x="AdoptionSpeed", y="desc_words", hue="Type", data=train);
plt.title('AdoptionSpeed by Type and count of Words in Description\n');
```

Interestingly pets with short text in ads are adopted quickly.
Or maybe longer descriptions mean more problems in the pets, therefore adoption speed is lower?
