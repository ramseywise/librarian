---
imported_hash: 604e62898ba47592
title: Ch02a   Python Environment Setup
summary: 'C:\> conda install pandas Solving environment: done'
order: 3
kind: notebook
section: Ch02   Python for Natural Language Processing
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch02 - Python for Natural Language Processing/Ch02a - Python Environment Setup.ipynb
---

```python
!python --version
```

```python
print('Welcome to Python')
```

```python
!pip freeze | grep pandas
```

```python
!pip install pandas
```

```python
!pip install pandas --upgrade
```

```

C:\> conda install pandas
Solving environment: done

## Package Plan ##

  environment location: C:\Program Files\Anaconda3

  added / updated specs:
    - pandas


The following packages will be downloaded:

    package                    |            build
    ---------------------------|-----------------
    pandas-0.23.3              |           py35_0         8.6 MB  conda-forge

The following packages will be UPDATED:

    pandas: 0.20.3-py35_1 conda-forge --> 0.23.3-py35_0 conda-forge

Proceed ([y]/n)? y


Downloading and Extracting Packages
pandas-0.23.3        |  8.6 MB | ########################################################### | 100%
Preparing transaction: done
Verifying transaction: done
Executing transaction: done
```

```python
!pip freeze | grep pandas
```

```
E:\>mkdir Apress
E:\>cd Apress
E:\Apress>pip install virtualenv
Collecting virtualenv
Installing collected packages: virtualenv
Successfully installed virtualenv-16.0.0

E:\Apress>mkdir test_proj && chdir test_proj

E:\Apress\test_proj>virtualenv venv
Using base prefix 'c:\\program files\\anaconda3'
New python executable in E:\Apress\test_proj\venv\Scripts\python.exe
Installing setuptools, pip, wheel...done.

E:\Apress\test_proj>echo 'This is Global System Python'
'This is Global System Python'

E:\Apress\test_proj>pip freeze | grep pandas
pandas==0.23.3



E:\Apress\test_proj>venv\Scripts\activate

(venv) E:\Apress\test_proj>echo 'This is VirtualEnv Python'
'This is VirtualEnv Python'

(venv) E:\Apress\test_proj>pip install pandas==0.21.0
Collecting pandas==0.21.0
    100% |################################| 9.0MB 310kB/s
Collecting pytz>=2011k (from pandas==0.21.0)
Collecting python-dateutil>=2 (from pandas==0.21.0)
Collecting numpy>=1.9.0 (from pandas==0.21.0)
Collecting six>=1.5 (from python-dateutil>=2->pandas==0.21.0)

Installing collected packages: pytz, six, python-dateutil, numpy, pandas
Successfully installed numpy-1.14.5 pandas-0.21.0 python-dateutil-2.7.3 pytz-2018.5 six-1.11.0

(venv) E:\Apress\test_proj>pip freeze | grep pandas
pandas==0.21.0

(venv) E:\Apress\test_proj>venv\Scripts\deactivate
E:\Apress\test_proj>pip freeze | grep pandas
pandas==0.23.3
```

http://docs.python-guide.org/en/latest/dev/virtualenvs/
