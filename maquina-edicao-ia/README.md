# Máquina de Edição IA · projeto de edição de vídeo

Projeto pronto para editar vídeos com IA (Claude Code ou Codex) e Remotion,
seguindo o método do **Guia do Aluno**: prepare, teste uma amostra, revise só o
trecho necessário e reutilize o padrão aprovado.

## O que já vem pronto

| Pasta / arquivo | Para quê |
|---|---|
| `CLAUDE.md` | Regras que o agente segue neste projeto (amostra antes do todo, não inventar dados, animação por frame, correção localizada, sem gastos extras). |
| `.claude/skills/` · `.agents/skills/` | As 3 skills bônus instaladas para Claude Code e Codex: briefing, legendas e enquadramento, revisão econômica. |
| `originais/` · `assets/` · `entregas/` | Organização da aula 2. Mídia não vai para o Git. |
| `projeto/` | Projeto Remotion com componentes reutilizáveis: apresentador com moldura animada, legendas, títulos, inserções e CTA. |
| `briefing/briefing-modelo.md` | Briefing em 7 partes (aula 4). |
| `padrao/padrao-visual.md` | Padrão visual reutilizável e checklist do próximo vídeo. |
| `comandos/COMANDOS.md` | Comandos do curso por etapa, adaptados a este projeto. |
| `fichas/*.csv` | Ficha de revisão, controle de custos e matriz de variações (separador `;`). |
| `roteiros/` | Roteiros de prática, incluindo dois de psicoeducação (TDAH no adulto, depressão sem resposta ao 1º tratamento). |

## Primeiros passos

```bash
cd projeto
npm install
npm run previa          # abre o Remotion Studio no navegador
```

No Studio, abra:

- **TesteInicial**: composição de 5 s da aula 2 ("Meu primeiro projeto").
- **demo-amostra** / **demo-completo**: demonstração do padrão sem gravação
  (legenda, título, moldura com inserção e CTA). Os tempos são estimados.

Instale também as skills técnicas oficiais do Remotion (uma vez):

```bash
npx skills add remotion-dev/skills
```

## Fluxo para um vídeo real

1. **Prepare.** Coloque a gravação em `originais/` e copie para
   `projeto/public/originais/`. Preencha `briefing/` a partir do modelo.
2. **Transcreva a fala real** (local e gratuito, Whisper.cpp):
   ```bash
   cd projeto
   npm run transcrever -- --video public/originais/MEU-VIDEO.mp4 --saida src/edicoes/meu-video.legendas.json
   ```
   Na primeira vez, baixa o Whisper e o modelo (`small`, centenas de MB). Para
   português técnico, `--modelo medium` erra menos. **Revise o JSON**: nomes,
   termos clínicos, números e acentos.
3. **Crie a edição.** Copie `src/edicoes/_modelo.ts` para
   `src/edicoes/meu-video-V01-simples.ts`, importe as legendas e registre em
   `src/edicoes/index.ts`. Ajuste `enquadramento` (ponto do rosto) e `amostra`.
4. **Teste.** Renderize a amostra de 8 s e assista no celular, com áudio:
   ```bash
   npx remotion render meu-video-V01-simples-amostra ../entregas/meu-video-V01-amostra.mp4
   ```
5. **Revise.** Anote trecho + problema + mudança em `fichas/ficha-de-revisao.csv`
   e peça só a correção daquele trecho (`comandos/COMANDOS.md`, seção 7).
6. **Exporte** só depois de aprovar o vídeo completo:
   ```bash
   npx remotion render meu-video-V01-simples-completo ../entregas/meu-video-final.mp4
   ```
7. **Reutilize.** Registre o que funcionou em `padrao/padrao-visual.md` e use
   uma nova edição (novo arquivo em `src/edicoes/`) para o próximo vídeo.

Na prática, você não precisa escrever código: envie ao agente os comandos de
`comandos/COMANDOS.md` e ele edita os arquivos de `src/edicoes/` seguindo o
`CLAUDE.md`.

## Como uma edição é descrita

```ts
export const meuVideo: Edicao = {
  id: 'meu-video-V01-simples',
  formato: 'vertical',                       // ou 'horizontal' (aulas 16:9)
  fps: 30,
  video: 'originais/meu-video.mp4',          // dentro de projeto/public
  duracaoSegundos: 0,                        // lida do arquivo quando há vídeo
  amostra: {inicio: 12, fim: 20},            // 8 s representativos
  enquadramento: {focoX: 50, focoY: 32, zoom: 1.05},
  moldura: [{inicio: 14.2, fim: 26.8}],      // apresentador vai para a moldura
  legendas,                                   // do JSON revisado
  titulos: [{inicio: 0.3, fim: 3.5, texto: 'Só distração?'}],
  insercoes: [{inicio: 15, fim: 26, arquivo: 'assets/tres-pontos.png', area: 'quadro-livre'}],
  cta: {inicio: 34, fim: 40, titulo: 'AGENDE SUA AVALIAÇÃO', apoio: '[CANAL REAL]'},
  demonstracao: false,
};
```

Cores, fontes, áreas seguras e posição da moldura ficam em
`projeto/src/tema.ts`. As fontes (Sora e Manrope, licença OFL) são locais, então
a renderização não depende da internet.

## Requisitos

Node.js LTS, npm e Git. Remotion: consulte a licença em
<https://www.remotion.dev/docs/license> (gratuita para uso individual).
Transcrição: compilador C++ (`make`/`g++` no Linux e macOS com Xcode CLT;
no Windows o Whisper.cpp vem pré-compilado).
