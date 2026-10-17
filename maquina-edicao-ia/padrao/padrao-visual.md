# Padrão visual aprovado

> Regras reutilizáveis entre vídeos. **Não** registre aqui textos, ofertas,
> nomes, números ou tempos de um vídeo específico — eles ficam no briefing e
> em `projeto/src/edicoes/`. Valores técnicos vivem em `projeto/src/tema.ts`.

Status: **rascunho inicial** (ainda não aprovado em vídeo real).

## Identidade

| Item | Valor |
|---|---|
| Fundo | `#0d0a1a` com grade discreta |
| Destaque | lilás `#a78bfa` · apoio ciano `#22d3ee` |
| Texto | `#f5f3ff` |
| Títulos | Sora 700, caixa alta, curtos (≤ 4 palavras) |
| Legendas / apoio | Manrope 700 |

## Legenda

- Até duas linhas; nunca esconder palavras (dividir o bloco).
- Vertical: 58 px, faixa a 400 px da borda inferior (margem para a interface).
- Com moldura ativa, a faixa sobe para logo acima da moldura.
- Fundo translúcido escuro, cantos 18 px.

## Enquadramento e moldura

- Tela cheia como base; rosto centralizado pelo ponto de foco (`enquadramento`).
- Moldura vertical: canto inferior direito, ~42% × 34% da tela, cantos
  arredondados, borda fina e sombra suave. Abrir só quando a explicação
  precisar de espaço; voltar à tela cheia ao terminar a ideia.
- Horizontal (aulas): moldura à direita, quadro explicativo à esquerda.

## Inserções e motion

- Uma inserção principal por vez, ligada a uma fala específica.
- Entrada com opacidade + deslocamento curto + escala suave; saída após a frase.
- Banner/CTA acima da cabeça, fixo até o fim (tempo de leitura).
- Título, card e ícones não disputam a mesma área.

## Quando um motion é necessário

Use quando a fala descreve **sequência, comparação, processo ou número
confirmado**. Não use para preencher tempo nem para repetir a legenda.

## Exportação

MP4 H.264, áudio AAC, 30 fps, mesma duração do projeto aprovado, em
`entregas/<nome>-<versão>.mp4`.

## Checklist curto para o próximo vídeo

- [ ] Original copiado para `projeto/public/originais/`, original preservado.
- [ ] Transcrição feita da gravação real e revisada (nomes, termos, números).
- [ ] Briefing preenchido; oferta e CTA conferidos.
- [ ] Amostra de 8 s aprovada em tamanho de celular, com áudio.
- [ ] Rosto e legenda livres em todas as transições de moldura.
- [ ] MP4 aberto fora da prévia: início, meio, fim, áudio e sincronização.
