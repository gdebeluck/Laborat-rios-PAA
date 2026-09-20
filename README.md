# Laboratórios de Projeto e Análise de Algoritmos

Repositório acadêmico com as soluções desenvolvidas para os laboratórios da disciplina de **Projeto e Análise de Algoritmos (PAA)**.

Os exercícios exploram a modelagem de problemas por meio de grafos, além da implementação e aplicação de algoritmos clássicos de busca e análise estrutural.

## Conteúdos

### Lab 1 - Grafos não direcionados

Implementação de um grafo não direcionado usando listas de adjacência. O laboratório utiliza uma busca em largura (BFS) para identificar ciclos ímpares e determinar se o grafo é bipartido.

Principais conceitos:

- Representação de grafos por listas de adjacência;
- Inserção e remoção de arestas;
- Vizinhança e grau de vértices;
- Busca em largura (BFS);
- Detecção de ciclos ímpares e reconhecimento de grafos bipartidos.

### Lab 2 - Grafos direcionados

Implementação de um grafo direcionado com suporte à construção do grafo reverso. A solução utiliza busca em profundidade (DFS) e o algoritmo de Kosaraju para analisar componentes fortemente conexos e calcular o número mínimo de bases necessárias para atender todas as cidades.

Principais conceitos:

- Representação de grafos direcionados;
- Busca em profundidade (DFS);
- Ordenação topológica;
- Grafo reverso;
- Componentes fortemente conexos;
- Algoritmo de Kosaraju.

## Organização do repositório

```text
.
├── lab1/
│   └── Lab1-Py/
│       └── Lab1-Py/
│           ├── grafo.py
│           ├── main.py
│           ├── autograder_tarefa1.py
│           ├── autograder_tarefa2.py
│           ├── casos/
│           └── integrantes.md
├── lab2/
│   └── lab2-Py/
│       ├── grafo.py
│       ├── main.py
│       ├── autograder_tarefa1.py
│       ├── autograder_tarefa2.py
│       ├── casos/
│       └── integrantes.md
└── README.md
```

Cada laboratório possui seus próprios casos de entrada e scripts de apoio para validação das tarefas.

## Tecnologias

- Python 3;
- Estruturas de dados para representação de grafos;
- Algoritmos BFS e DFS;
- Testes com arquivos de entrada e autograders fornecidos nas pastas dos laboratórios.

## Como executar

Entre na pasta do laboratório desejado e execute o arquivo principal:

```bash
cd lab1/Lab1-Py/Lab1-Py
python main.py < casos/caso01.in
```

Para o segundo laboratório:

```bash
cd lab2/lab2-Py
python main.py < casos/caso01.in
```

Os arquivos de entrada seguem o formato definido nos enunciados de cada tarefa.

## Objetivo acadêmico

Este repositório registra a evolução prática no desenvolvimento de soluções algorítmicas, com foco em:

- abstração e modelagem de problemas;
- escolha de estruturas de dados adequadas;
- análise de algoritmos em grafos;
- organização de código Python;
- validação de soluções por meio de casos de teste.

## Colaboração

Os integrantes de cada laboratório estão listados no arquivo `integrantes.md` correspondente.

Este projeto faz parte do meu percurso acadêmico e reúne exemplos práticos de implementação de algoritmos fundamentais para a resolução de problemas computacionais.