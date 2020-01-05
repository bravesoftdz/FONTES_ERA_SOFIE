# rest_service
Servidor REST dinâmico do MySofie

O propósito deste servidor é o de carregar dinâmicamente manipuladores HTTP, além de outros artefatos. 


**Parâmetros de execução:**


**-d ou --debug    :** Executa o servidor em modo debug  
**-p ou --port     :** Especifica a porta TCP para servidão HTTP  
**-m ou --manifest :** Aponta para um módulo Python que devolve a lista de manipuladores HTTP e efetivamente estende a solução 

# Exemplo de Manifesto válido

```python
# coding: utf-8

from os import walk, path
from runpy import run_path

URLS2BRAIN = [] #: Lista com os manipuladores HTTP

VERSION = 'MySofie/2018.04.11' #: Versão so servidor que trafegará no cabeçalho Server 

API_VERSION = '/api/v1' #: Versão da API que comporá as URLs  

ALL_PATHS = walk(path.dirname(path.realpath(__file__)))

for root, dirs, files in ALL_PATHS:
    for file in files:
        if file == card.py:
            data = run_path(path.join(root, file))
            if 'HANDLERS' in data:
                URLS2BRAIN.extend(data['HANDLERS'])

for each in URLS2BRAIN:
    if each[0][0] != '/':
        each[0] = '/' + each[0]
    each[0] = API_VERSION + each[0]
```

