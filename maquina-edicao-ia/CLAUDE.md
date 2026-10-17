# Projeto de edição de vídeo · Máquina de Edição IA

Instruções para o agente (Claude Code ou Codex) neste projeto. Leia antes de
qualquer edição. Elas resumem o método do Guia do Aluno: **Prepare → Teste →
Revise → Reutilize**.

## Estrutura (não altere sem pedido)

```text
originais/   gravações brutas. NUNCA editar, mover ou sobrescrever.
assets/      fotos, logos, banners, ícones autorizados pelo usuário.
projeto/     projeto Remotion editável (src = código, public = mídia usada).
entregas/    MP4 finais exportados. Não sobrescrever entregas aprovadas.
briefing/    briefing de cada vídeo (preencher antes de editar).
padrao/      padrão visual aprovado e checklist de revisão.
fichas/      ficha de revisão, controle de custos e matriz de variações (CSV).
comandos/    comandos prontos do curso, por etapa.
roteiros/    roteiros de gravação.
```

Para usar um original na composição, **copie** de `originais/` para
`projeto/public/originais/` (o original fica preservado). Assets vão para
`projeto/public/assets/`.

## Skills

- Bônus do curso (em `.claude/skills/` e `.agents/skills/`):
  `meia-briefing-de-edicao`, `meia-legendas-e-enquadramento`,
  `meia-revisao-economia`. Use a skill da etapa atual; não carregue todas.
- Técnica oficial: `remotion-best-practices` (instale com
  `npx skills add remotion-dev/skills`). Antes de implementar, verifique se
  está disponível e carregue as referências pertinentes. **Se estiver ausente,
  diga isso e consulte a documentação oficial; nunca afirme ter usado uma
  skill inexistente.**

## Como o projeto Remotion funciona

- Cada vídeo é um arquivo de dados em `projeto/src/edicoes/<nome>.ts`
  (tipo `Edicao` em `src/tipos.ts`): vídeo, legendas, títulos, inserções,
  intervalos de moldura, CTA e trecho de amostra. Registre em
  `src/edicoes/index.ts`. Cada edição gera `<id>-amostra` e `<id>-completo`.
- Visual centralizado em `src/tema.ts` (cores, fontes, áreas seguras,
  moldura). Mudou o padrão? Atualize também `padrao/padrao-visual.md`.
- Legendas: `npm run transcrever -- --video public/originais/X.mp4 --saida
  src/edicoes/X.legendas.json` (Whisper local). O roteiro serve só para
  conferir termos — **a gravação é a fonte da fala**.
- Versões: um arquivo por versão (`aula01-V01-simples.ts`,
  `aula01-V02-insercoes.ts`). Nunca sobrescreva uma versão aprovada.

## Regras inegociáveis

1. **Amostra antes do vídeo inteiro.** Primeiro ~8 s representativos (fala,
   legenda, enquadramento e uma inserção, se houver). Aguarde aprovação antes
   de aplicar ao restante e antes de exportar.
2. **Animação só pelo frame do Remotion** (`useCurrentFrame`, `interpolate`,
   `spring`). Sem CSS animations, relógio independente ou `useFrame` para
   controlar movimento. Prévia e MP4 devem ser idênticos.
3. **Não inventar dados.** Preço, resultado, depoimento, prazo, número,
   métrica, CTA: só o que o usuário forneceu e conferiu. Lacuna factual fica
   como lacuna. Conteúdo de saúde: sem promessa de resultado, sem antes e
   depois, sem prescrição.
4. **Preservar** voz, sentido da fala, original e tudo que já foi aprovado.
   Não cortar automaticamente trechos que mudem o sentido.
5. **Legenda:** até duas linhas, contraste, sem cobrir rosto, com margem para
   a interface da plataforma. Nunca esconder palavras (divida o bloco).
6. **Rosto:** centralizado em tela cheia e na moldura; não cortar cabeça,
   queixo ou gestos importantes.
7. **Correção localizada:** trecho + problema + mudança + o que preservar.
   Gere prévia só do trecho alterado com as transições de entrada e saída.
8. **Erro repetido:** pare, diagnostique a causa, teste uma hipótese por vez
   no menor trecho. Não refaça o vídeo inteiro como tentativa.
9. **Sem gastos extras:** não contratar serviços, comprar créditos, usar API
   paga ou render em nuvem sem aprovação específica. Não estimar consumo,
   saldo ou custo por vídeo sem dados.
10. **Relatar com evidência:** diga qual intervalo e arquivo foram realmente
    verificados. Frames estáticos não comprovam sincronização.

## Comandos do projeto (em `projeto/`)

```bash
npm install                      # uma vez
npm run previa                   # Remotion Studio (prévia no navegador)
npm run verificar                # checagem de tipos
npx remotion render <id>-amostra ../entregas/<id>-amostra.mp4
npx remotion render <id>-completo ../entregas/<id>-final.mp4   # só após aprovação
```

Exportação padrão: MP4 H.264, áudio AAC, 1080 × 1920 (ou 1920 × 1080),
mesma duração e taxa de quadros aprovadas. Abra o MP4 fora da prévia para
conferir. Saída existente não é sobrescrita (use outro nome de versão).
