# Article Infographic

Transforma um artigo científico ou médico (PDF) em um **infográfico de uma página**:
manchete, resumo em uma frase, números-chave, desenho do estudo (PICO), fluxo do
estudo, principais achados com suas estatísticas, gráficos gerados a partir das
tabelas do artigo, mensagens para levar, implicações clínicas, limitações,
glossário e a **referência completa** (autores, título, periódico, ano, DOI).

O pipeline tem três etapas, cada uma com um contrato Pydantic:

| Etapa | Módulo | O que faz |
|---|---|---|
| Extração | `extract.py` | Converte o arquivo com o **Docling** e monta `ArticleExtraction`: metadados, seções classificadas (resumo, introdução, métodos, resultados, discussão, conclusão), tabelas, figuras e estatísticas encontradas no texto (p, IC 95%, OR/RR/HR, n, %, média ± DP). |
| Síntese | `synthesis/` | Produz `InfographicSpec`. Três backends: `heuristic` (sem modelo, sem rede), `ollama` (LLM local, ex. Jetson/Raspberry) e `anthropic` (Claude, SDK oficial). Os backends com LLM devolvem JSON validado e caem para o heurístico em caso de falha. |
| Renderização | `render.py`, `charts.py` | Gera um HTML autocontido (claro/escuro, pronto para imprimir em A3) com gráficos SVG inline: barras, rosca, dumbbell (antes/depois) e forest plot (efeitos com IC). |

Os gráficos das tabelas são construídos por regras conservadoras (`table_charts.py`):
só entram colunas majoritariamente numéricas que compartilham a mesma escala; colunas
`OR (IC 95%)` viram forest plot, pares `baseline / week 12` viram dumbbell e
percentuais que somam 100 viram rosca.

## Instalação

Dentro do repositório docling (ambiente já criado com `make setup`):

```bash
uv run --no-sync pip install -e apps/article_infographic          # ou
uv pip install -e "apps/article_infographic[anthropic,pdf]"
```

Como pacote independente em qualquer máquina:

```bash
pip install "docling[standard]" -e apps/article_infographic
pip install anthropic          # opcional: backend Claude
pip install playwright && playwright install chromium   # opcional: exportar PDF
```

Na primeira conversão de PDF o Docling baixa os modelos de layout e estrutura de tabelas
(Hugging Face). DOCX, HTML, Markdown e JSON do Docling não precisam de modelos.

## Uso

```bash
# 1. Sem LLM (rápido, determinístico, nunca inventa números)
article-infographic build artigo.pdf -o infograficos/

# 2. LLM local via Ollama (ex.: Jetson Orin Nano com qwen3)
article-infographic build artigo.pdf --backend ollama --model qwen3:8b --host http://jetson:11434

# 3. Claude (usa ANTHROPIC_API_KEY ou perfil do `ant auth login`)
article-infographic build artigo.pdf --backend anthropic --lang pt --pdf

# 4. Editar o JSON gerado à mão e renderizar de novo
article-infographic render infograficos/artigo.infographic.json -o poster.html

# 5. Aplicativo web local (upload do PDF pelo navegador)
article-infographic serve --port 8765 --backend ollama --model qwen3:8b
```

Saídas de `build`:

- `artigo.infographic.html` – o pôster (abra no navegador; **Imprimir / PDF** gera o PDF em A3).
- `artigo.infographic.json` – o `InfographicSpec`; edite e use `render`.
- `artigo.extraction.json` – a extração bruta do Docling (útil para RAG ou auditoria).

Também funciona como módulo: `python -m article_infographic build artigo.pdf`.

## API em Python

```python
from pathlib import Path
from article_infographic import build_infographic

result = build_infographic(Path("artigo.pdf"), Path("out"), backend="ollama", model="qwen3:8b", language="pt")
print(result.spec.one_sentence_summary)
print(result.spec.reference)
```

## Backends de síntese

| Backend | Requisitos | Comportamento |
|---|---|---|
| `heuristic` | nenhum | Seleciona frases do próprio artigo (resultados com estatística, conclusão, limitações citadas pelos autores). Nunca parafraseia. |
| `ollama` | servidor Ollama (`OLLAMA_HOST`, `OLLAMA_MODEL`) | `/api/chat` com `format` = JSON Schema de `LLMInfographicDraft`; contexto de 32k tokens por padrão. |
| `anthropic` | `pip install anthropic` + credenciais | `client.messages.parse` com saída estruturada; modelo padrão `claude-opus-5` (`ANTHROPIC_MODEL` para trocar). Recusas são tratadas explicitamente. |

Nos dois backends com LLM, os metadados, a referência e os gráficos das tabelas vêm do
código (exatos por construção); o modelo escreve apenas o conteúdo interpretativo e é
instruído a usar somente números presentes no artigo.

## Testes

```bash
uv run --no-sync pytest apps/article_infographic/tests
```

Os testes usam a saída real do Docling para um artigo em PDF (`tests/data/pdf/groundtruth/2206.01062.json`)
e um ensaio clínico sintético em Markdown (`tests/data/sertraline_trial.md`) que exercita p-valores,
IC, OR, tabelas de desfechos, forest plot e dumbbell. Um exemplo renderizado está em `examples/`.

## Limitações conhecidas

- A identificação de autores/periódico é heurística; confira sempre a referência no pôster.
- Legendas de tabelas em Markdown não são vinculadas às tabelas (o título do gráfico vira "Dados da Tabela N").
- O backend heurístico não traduz: as frases ficam no idioma do artigo; apenas os rótulos seguem `--lang`.
