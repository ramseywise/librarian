---
imported_hash: ba6299f12e86f864
title: Wait for the file to finish processing
summary: genai.configure(apikey=os.environ["GEMINIAPIKEY"])
order: 3
kind: notebook
section: Notebooks
source: learn-ai-engineering/ai-engineering/01-prompt-engineering/notebooks/gemini-context-caching.ipynb
---

```python
%%capture
pip install -q -U google-generativeai
```

```python
from google.generativeai import caching
import google.generativeai as genai
import os
import time
import datetime

from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
```

```python
file_name = "weekly-ai-papers.txt"
file  = genai.upload_file(path=file_name)
```

```python
# Wait for the file to finish processing
while file.state.name == "PROCESSING":
    print('Waiting for video to be processed.')
    time.sleep(2)
    video_file = genai.get_file(file.name)
```

```python
print(f'File processing complete: ' + file.uri)
```

```python
# Create a cache with a 5 minute TTL
cache = caching.CachedContent.create(
    model="models/gemini-1.5-flash-001",
    display_name="ml papers of the week", # used to identify the cache
    system_instruction="You are an expert AI researcher, and your job is to answer user's query based on the file you have access to.",
    contents=[file],
    ttl=datetime.timedelta(minutes=15),
)

# create the model
model = genai.GenerativeModel.from_cached_content(cached_content=cache)
```

```python
# query the model
response = model.generate_content(["Can you please tell me the latest AI papers of the week?"])

print(response.text)
```

```python
response = model.generate_content(["Can you list the papers that mention Mamba? List the title of the paper and summary."])
print(response.text)
```

```python
response = model.generate_content(["What are some of the innovations around long context LLMs? List the title of the paper and summary."])
print(response.text)
```
