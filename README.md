# SaúdeScope

**Análise Preditiva de Perfis Epidemiológicos para Gestão Estratégica em Clínicas Multiprofissionais de Saúde**

Projeto Integrador do curso de Ciência de Dados da Universidade Virtual do Estado de São Paulo (UNIVESP).

## Contexto

Clínicas multiprofissionais de saúde atendem públicos de todas as idades, mas raramente têm dados estruturados sobre o perfil de saúde da população da região. O SaúdeScope usa **apenas dados abertos** da Pesquisa Nacional de Saúde (PNS) 2019, do IBGE, para estimar a prevalência de doenças crônicas e condições de saúde mental no Estado de São Paulo e apoiar o planejamento de uma clínica multiprofissional em Itapetininga (SP). Nenhum dado de paciente é utilizado.

## Principais resultados (PNS 2019, Estado de São Paulo, prevalências ponderadas)

| Condição | Prevalência |
|---|---|
| Hipertensão | 28,2% |
| Depressão | 12,4% |
| Diabetes | 10,3% |
| Outra doença mental | 7,7% |
| AVC/derrame | 2,1% |
| Insuficiência renal crônica | 1,4% |

- Sobrepeso e obesidade somam 67,7% dos adultos e idosos (obesidade: 36,3%).
- 8,2% dos adultos e idosos têm duas ou mais doenças crônicas ao mesmo tempo.
- Modelo de triagem de risco de hipertensão (regressão logística): AUC-ROC de 0,80. Com o limiar de decisão ajustado para cerca de 0,30, o recall é de aproximadamente 73% e a precisão de aproximadamente 53%.

## Estrutura do repositório

```
saudescope/
├── notebooks/
│   ├── 01_ingestao_e_leitura.ipynb      leitura dos microdados em largura fixa
│   ├── 02_limpeza_e_tratamento.ipynb    recodificação, IMC, prevalência ponderada
│   ├── 03_analise_exploratoria.ipynb    desigualdades, multimorbidade, correlações
│   ├── 04_modelagem_ml.ipynb            comparação de 4 modelos de classificação
│   └── 05_avaliacao_final.ipynb         ajuste do limiar e consolidação de insights
├── data/
│   ├── raw/                             PNS_2019.txt (não versionado) e layout SAS
│   └── processed/                       tabelas tratadas, modelo e configurações
├── scripts/
│   └── upload_supabase.py               envia as tabelas para o banco online
├── src/                                 funções auxiliares
├── docs/                                relatórios e resumos
└── requirements.txt
```

## Como reproduzir

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Baixe os microdados da PNS 2019 no site do IBGE e coloque `PNS_2019.txt` e `input_PNS_2019.sas` em `data/raw/`.
3. Execute os notebooks na ordem, de `01` a `05`. Os notebooks usam o caminho relativo `data/processed`. Se o Jupyter não encontrar a pasta `data`, crie um atalho dentro de `notebooks/` (no Windows: `mklink /J notebooks\data data`, executado na raiz do projeto).

## Banco de dados online (Supabase)

O script `scripts/upload_supabase.py` cria seis tabelas no Postgres do Supabase:

| Tabela | Conteúdo |
|---|---|
| `pessoas_pns_sp` | 17.522 pessoas entrevistadas, com variáveis tratadas |
| `resumo_prevalencias` | prevalência bruta e ponderada por condição |
| `resultados_modelos` | métricas dos modelos de Machine Learning |
| `dicionario_variaveis` | dicionário das variáveis selecionadas |
| `insights_saudescope` | achados organizados por especialidade |
| `config_modelo` | parâmetros do modelo final |

A senha do banco **não** fica no código: o script a solicita ao ser executado, ou lê a variável de ambiente `SUPABASE_PASSWORD`.

## Limitações

- A PNS não permite desagregação por município. O Estado de São Paulo é usado como referência regional para Itapetininga.
- O modelo é uma ferramenta de **triagem populacional**. Ele não substitui o diagnóstico clínico individual.
- As medidas de peso e altura aferidas existem apenas para um subconjunto da amostra, e isso limita as análises de IMC.
- Os diagnósticos são autorreferidos.

## Fonte dos dados

IBGE. *Pesquisa Nacional de Saúde 2019*. Rio de Janeiro: IBGE, 2020. Disponível em: https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html

## Equipe

André Luiz dos Santos, Carlos Alan Costa Almeida, Henrique Pinheiro Alencar, Kaue William Miranda de Souza, Keila Maiamy Dias Coimbra, Leonardo Santos da Cunha, Marco Aurélio Costa da Silva e Thais Karoline Bento Monteiro da Silva.
