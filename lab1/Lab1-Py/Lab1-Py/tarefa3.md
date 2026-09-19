# Tarefa 3

Preencha abaixo a análise de complexidade da sua implementação dos seguintes métodos da classe Grafo, conforme especificado no PDF.

Complexidade: O(min(u, v))

onde u = grau do vértice 1 e v = grau do vértice 2.

Acesso ao dicionário: O(1)
    Busca em dicionário hash é constante

Busca de u: O(v)
   Busca linear: percorre até encontrar u ou chegar ao fim
   No pior caso: O(d_v) - quando u não está no final ou não existe

Acesso ao dicionário: O(1)
   Busca em dicionário hash é constante

Busca de v: O(u)
   Busca linear: percorre até encontrar v ou chegar ao fim
   No pior caso: O(u)

Melhor Caso: O(1)

Pior Caso: O(v + u)

## Método Vizinhos

Complexidade: O(1)

Acesso ao dicionário: O(1)
   Tabela hash com acesso direto mediante chave
