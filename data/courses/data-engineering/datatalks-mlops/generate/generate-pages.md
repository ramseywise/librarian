---
imported_hash: 869ed7e1a71ac3d9
title: '{moduleinfo[''number'']}. {moduleinfo[''title'']}'
summary: from pathlib import Path from urllib.parse import urlparse, parse_qs
order: 34
kind: notebook
section: Generate
source: learn-ai-engineering/data-engineering/DataTalks MLOps/generate/generate_pages.ipynb
---

```python
import io
import json

from pathlib import Path
from urllib.parse import urlparse, parse_qs

import pandas as pd
import numpy as np

import requests
import clipboard

from PIL import Image
from jinja2 import Template
```

```python
module_number = 3
module_title = 'Orchestration and ML Pipelines'
module_folder = Path('..') / '03-orchestration'

meta_json_file = module_folder / 'meta.json'
playlist_id = 'PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK'
```

```python
module_number = 5
module_title = 'ML Monitoring'
module_folder = Path('..') / '05-monitoring'

meta_json_file = module_folder / 'meta.json'
playlist_id = 'PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK'
```

```python
module_number = 6
module_title = 'Best Practices'
module_folder = Path('..') / '06-best-practices'

meta_json_file = module_folder / 'meta.json'
playlist_id = 'PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK'
```

```python
module_number = 4
module_title = 'Model Deployment'
module_folder = Path('..') / '04-deployment'

meta_json_file = module_folder / 'meta.json'
playlist_id = 'PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK'
```

## Prepare `meta.json` info

```python
text = """
module_number	module_title	unit_number	unit_title	full_title	youtube
5	Monitoring	1	Intro to ML monitoring	MLOps Zoomcamp 5.1 - Intro to ML monitoring	https://www.youtube.com/watch?v=SQ0jBwd_3kk
5	Monitoring	2	Environment setup	MLOps Zoomcamp 5.2 - Environment setup	https://www.youtube.com/watch?v=yixA3C1xSxc
5	Monitoring	3	Prepare reference and model	MLOps Zoomcamp 5.3 - Prepare reference and model	https://www.youtube.com/watch?v=IjNrkqMYQeQ
5	Monitoring	4	Evidently metrics calculation	MLOps Zoomcamp 5.4 - Evidently metrics calculation	https://www.youtube.com/watch?v=kP3lzh_HfWY
5	Monitoring	5	Dummy monitoring	MLOps Zoomcamp 5.5 - Dummy monitoring	https://www.youtube.com/watch?v=s3G4PMsOMOA
5	Monitoring	6	Data quality monitoring	MLOps Zoomcamp 5.6 - Data quality monitoring	https://www.youtube.com/watch?v=fytrmPbcLhI
5	Monitoring	7	Save Grafana Dashboard	MLOps Zoomcamp 5.7 - Save Grafana Dashboard	https://www.youtube.com/watch?v=-c4iumyZMyw
5	Monitoring	8	Debugging with test suites and reports	MLOps Zoomcamp 5.8 - Debugging with test suites and reports	https://www.youtube.com/watch?v=sNSk3ojISh8""".strip()
```

```python
df = pd.read_csv(io.StringIO(text), delimiter='\t')
```

```python
df['youtube'] = df['youtube'].fillna('')
```

```python
df_units = df[['unit_number', 'unit_title', 'youtube']]
units = df_units \
    .rename(columns={'unit_number': 'number', 'unit_title': 'title'}) \
    .to_dict(orient='records')
units
```

```python
meta = {
    'module': {
        'number': module_number,
        'title': module_title
    },
    'units': units
}
```

```python
meta
```

```python
module_folder.mkdir(parents=True, exist_ok=True)

with open(meta_json_file, 'wt') as f_out:
    json.dump(meta, f_out, indent=2)
```

```python
!head {meta_json_file}
```

## Generate page

module_folder = Path('..') / '05-monitoring'
meta_json_file = module_folder / 'meta.json'
playlist_id = 'PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK'

```python
with meta_json_file.open('rt') as f_in:
    meta = json.load(f_in)
```

```python
module_info = meta['module']
units = meta['units']
```

```python
module_info
```

```python
images_folder = module_folder / 'images'
images_folder.mkdir(parents=True, exist_ok=True)
```

```python
template_string = """
## {{ module_number }}.{{ unit_number }} {{ unit_title }}

{% if youtube %}<a href="{{ youtube }}">
  <img src="{{ thumbnail }}">
</a>{% endif %}{% if not youtube %}COMING SOON{% endif %}


""".lstrip()

template = Template(template_string)
```

```python
def download_thumbnail(video, module, unit, folder):
    if type(unit) in [int, np.int64]:
        thumbnail_file = f'thumbnail-{module}-{unit:02d}.jpg'
    else:
        thumbnail_file = f'thumbnail-{module}-{unit}.jpg'

    thumbnail_file = folder / thumbnail_file

    if thumbnail_file.exists():
        print(f'{thumbnail_file} exists')
        return thumbnail_file

    video_id = parse_qs(urlparse(video).query)['v'][0]
    print(f'processing video {video_id}...')
    thumbnail_url = f'https://img.youtube.com/vi/{video_id}/0.jpg'

    response = requests.get(thumbnail_url)
    thumbnail = Image.open(io.BytesIO(response.content))
    w_img, h_img = thumbnail.size

    play = Image.open(Path('../images/play.png'))
    w_play, h_play = play.size

    x0 = w_img // 2 - w_play // 2
    y0 = h_img // 2 - h_play // 2

    thumbnail.paste(play, (x0, y0), play)
    thumbnail.save(thumbnail_file, quality=90)

    print('saved to', thumbnail_file)

    return thumbnail_file
```

```python
module_number = module_info['number']

parts = []

for unit in units:
    unit_number = unit['number']

    params = {
        'module_number': module_info['number'],
        'module_name': module_info['title'],
        'unit_number': unit['number'],
        'unit_title': unit['title']
    }

    if 'youtube' in unit:
        youtube = unit['youtube']
        if len(youtube) and youtube.startswith('https'):
            thumbnail = download_thumbnail(youtube, module_number, unit_number, images_folder)
            thumbnail_path = '/'.join(thumbnail.parts[2:])
            params['youtube'] = f'{youtube}&list={playlist_id}'
            params['thumbnail'] = thumbnail_path

    template_string = template.render(params)
    print(template_string)
    parts.append(template_string)
```

```python
prefix = f"""
# {module_info['number']}. {module_info['title']}
""".strip()


final_result = '\n\n'.join([prefix] + parts)
```

```python
clipboard.copy(final_result)
```
