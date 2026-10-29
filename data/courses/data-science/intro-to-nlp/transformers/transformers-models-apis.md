---
imported_hash: ae190deb33c9f8d6
title: using default model and tokenizer for the task
summary: Using Transformers (v2.3.0) APIs - State-of-the-art Natural Language Processing for Pytorch and TensorFlow 2.0.
order: 23
kind: notebook
section: Transformers
source: learn-ai-engineering/data-science/intro-to-nlp/transformers/transformers_models_apis.ipynb
---

## Transformers NLP Models

Using **Transformers** (v2.3.0) APIs - State-of-the-art Natural Language Processing for Pytorch and TensorFlow 2.0.

**Transformers** provides general-purpose architectures that include BERT, GPT-2, RoBERTa, XLM, DistilBert, XLNet for Natural Language tasks.

- ***Sentence Classification / Sentiment Analysis***
- ***Token Classification***
- ***Question-Answering***
- ***Summarization***
- ***Translation***
- ***Feature Extraction***

**Using the Pipelines**

```python
from transformers import pipeline

# using default model and tokenizer for the task
pipeline("<task-name>")

# using a user-specified model
pipeline("<task-name>", model="<model_name>")

# using custom model/tokenizer as str
pipeline('<task-name>', model='<model name>', tokenizer='<tokenizer_name>')
```

**NLP tasks**

- **Tokenization**: Splits the initial input into multiple sub-entities (tokens).
- **Inference**: Maps tokens into a more meaningful representation.
- **Decoding**: Uses the above representation to generate and/or extract the final output for the underlying task.

```python
# chevking python version
! python -V
```

```python
# installing transformers
!pip install -q transformers
```

```python
# importing packages
from __future__ import print_function
from transformers import pipeline

import ipywidgets as widgets
import numpy as np
import warnings

warnings.filterwarnings('ignore')
```

## 1. Sentence Classification - Sentiment Analysis
Indicates if the overall sentence is either *positive* or *negative*.

```python
nlp_sent_classification = pipeline('sentiment-analysis')
nlp_sent_classification('It is a sunny day today !')
```

## 2. Token Classification - Named Entity Recognition

Assigns a label for each token in the input.

```python
nlp_token_class = pipeline('ner')
nlp_token_class('Hugging Face is a French company based in New-York.')
```

## 3. Question Answering
Based on a ***question*** x ***context*** tuple, the model finds a span of text in **content** answering the **question**.

```python
nlp_q_a = pipeline('question-answering')
nlp_q_a(context='Hugging Face is a French company based in New-York.', question='Where is based Hugging Face ?')
```

## 4. Text Generation - Mask Filling

Suggests possible word or words to fill a masked input with respect to the provided **context**.

```python
nlp_mask_fill = pipeline('fill-mask')
nlp_mask_fill('Hugging Face is a French company based in ' + nlp_mask_fill.tokenizer.mask_token)
```

## 5. Summarization
Summarizes a text to a shorter text. Supported by **Bart** and **T5**.

```python
text = """
New York (CNN)When Liana Barrientos was 23 years old, she got married in Westchester County, New York.
A year later, she got married again in Westchester County, but to a different man and without divorcing her first husband.
Only 18 days after that marriage, she got hitched yet again. Then, Barrientos declared "I do" five more times, sometimes only within two weeks of each other.
In 2010, she married once more, this time in the Bronx. In an application for a marriage license, she stated it was her "first and only" marriage.
Barrientos, now 39, is facing two criminal counts of "offering a false instrument for filing in the first degree," referring to her false statements on the
2010 marriage license application, according to court documents.
Prosecutors said the marriages were part of an immigration scam.
On Friday, she pleaded not guilty at State Supreme Court in the Bronx, according to her attorney, Christopher Wright, who declined to comment further.
After leaving court, Barrientos was arrested and charged with theft of service and criminal trespass for allegedly sneaking into the New York subway through an emergency exit, said Detective
Annette Markowski, a police spokeswoman. In total, Barrientos has been married 10 times, with nine of her marriages occurring between 1999 and 2002.
All occurred either in Westchester County, Long Island, New Jersey or the Bronx. She is believed to still be married to four men, and at one time, she was married to eight men at once, prosecutors say.
Prosecutors said the immigration scam involved some of her husbands, who filed for permanent residence status shortly after the marriages.
Any divorces happened only after such filings were approved. It was unclear whether any of the men will be prosecuted.
The case was referred to the Bronx District Attorney\'s Office by Immigration and Customs Enforcement and the Department of Homeland Security\'s
Investigation Division. Seven of the men are from so-called "red-flagged" countries, including Egypt, Turkey, Georgia, Pakistan and Mali.
Her eighth husband, Rashid Rajput, was deported in 2006 to his native Pakistan after an investigation by the Joint Terrorism Task Force.
If convicted, Barrientos faces up to four years in prison.  Her next court appearance is scheduled for May 18.
"""

nlp_summarizer = pipeline('summarization')
nlp_summarizer(text)
```

## 6. Translation
Translates a text input from a language to another language.
Translation is supported by **T5**.

```python
# translating from English to French
nlp_translator = pipeline('translation_en_to_fr')
nlp_translator("HuggingFace is a French company that is based in New York City. HuggingFace's mission is to solve NLP one commit at a time")
```

```python
# translating from English to German
nlp_translator = pipeline('translation_en_to_de')
nlp_translator("The history of natural language processing (NLP) generally started in the 1950s, although work can be found from earlier periods.")
```

## 7. Text Generation
Generates text based on an input. Text generation is currently supported by GPT-2, OpenAi-GPT, TransfoXL, XLNet, CTRL and Reformer.

```python
nlp_text_generation = pipeline("text-generation")
nlp_text_generation("Today is a beautiful day and I will")
```

## 8. Features Extraction
Maps the input to a higher, multi-dimensional space learned from the data.

```python
nlp_features = pipeline('feature-extraction')
output = nlp_features('Hugging Face is a French company based in Paris')
np.array(output).shape
```

**Pipelines**

```python
task = widgets.Dropdown(
    options=['sentiment-analysis', 'ner', 'fill_mask'],
    value='sentiment-analysis',
    description='Task:',
    disabled=False
)

input = widgets.Text(
    value='',
    placeholder='Enter something',
    description='Your input:',
    disabled=False
)

def forward(_):
    if len(input.value) > 0:
        if task.value == 'ner':
            output = nlp_token_class(input.value)
        elif task.value == 'sentiment-analysis':
            output = nlp_sentence_classif(input.value)
        else:
            if input.value.find('<mask>') == -1:
                output = nlp_fill(input.value + ' <mask>')
            else:
                output = nlp_fill(input.value)
        print(output)

input.on_submit(forward)
display(task, input)
```

```python
context = widgets.Textarea(
    value='Einstein is famous for the general theory of relativity',
    placeholder='Enter something',
    description='Context:',
    disabled=False
)

query = widgets.Text(
    value='Why is Einstein famous for ?',
    placeholder='Enter something',
    description='Question:',
    disabled=False
)

def forward(_):
    if len(context.value) > 0 and len(query.value) > 0:
        output = nlp_qa(question=query.value, context=context.value)
        print(output)

query.on_submit(forward)
display(context, query)
```
