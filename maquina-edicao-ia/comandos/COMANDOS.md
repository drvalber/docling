# Comandos por etapa

Comandos do Guia do Aluno (Máquina de Edição IA), adaptados aos caminhos deste
projeto. Substitua os campos entre colchetes antes de enviar. Envie **um comando
por vez** e confira o resultado antes do próximo.

Fluxo: **Prepare → Teste (amostra 8 s) → Revise (trecho) → Reutilize (padrão)**.

Bloco técnico que acompanha os pedidos de edição (cole junto quando o comando
pedir "+ BLOCO TÉCNICO"):

```text
Antes de implementar, verifique se a skill remotion-best-practices está disponível,
carregue-a e leia as referências pertinentes. Se ela estiver ausente, informe isso e
consulte a documentação oficial; não afirme ter usado uma skill inexistente. Confira a
compatibilidade das versões do projeto. Anime elementos pela timeline e pelos frames do
Remotion, sem CSS animations, relógio independente ou useFrame para controlar movimento.
Não use serviços pagos extras sem autorização.
```

---

## 1 · Preparar (aulas 2–4)

### Verificar o ambiente
```text
Quero preparar este computador para editar vídeos locais com Remotion. Verifique o
sistema, a pasta de trabalho e a disponibilidade do Node.js, npm e Git. Diga o que já
está pronto e o que falta. Para cada item ausente, explique o próximo passo em linguagem
simples e use a documentação oficial atual. Não atualize nem substitua instalações que
já funcionam sem explicar a necessidade. Ao terminar, rode `npm install` e
`npm run verificar` em projeto/, sem criar a edição ainda.
```

### Instalar as skills oficiais do Remotion
```text
Instale as skills oficiais de remotion-dev/skills seguindo a documentação atual em
https://www.remotion.dev/docs/ai/skills (comando publicado: npx skills add remotion-dev/skills)
e o procedimento compatível com este agente. Confirme que estão disponíveis junto com as
3 skills bônus em .claude/skills e diga como serão usadas. Não altere o projeto.
```

### Abrir a primeira prévia
```text
Em projeto/, abra o Remotion Studio (npm run previa) e a composição TesteInicial
(5 s, "Meu primeiro projeto"). Informe o endereço para eu abrir. Não exporte MP4.
```

### Organizar os materiais
```text
O vídeo deste trabalho é originais/[ARQUIVO]. Copie-o para projeto/public/originais/
preservando a origem, e os assets que vamos usar de assets/ para projeto/public/assets/.
Evite duplicações desnecessárias e informe onde ficou cada material.
```

### Retomar o projeto
```text
Estou retomando este projeto na mesma pasta. Identifique as edições existentes em
projeto/src/edicoes e abra a prévia. Preserve a configuração e os arquivos; não crie um
novo projeto nem reinstale o que já funciona.
```

### Definir a regra de gastos
```text
Neste projeto, meu teto de gastos extras no período [PERÍODO] é [VALOR E MOEDA]. Use
ferramentas locais e os assets fornecidos sempre que forem suficientes. Não contrate
serviços, compre créditos nem use uma API paga adicional sem minha aprovação específica.
Se a tarefa depender disso, apresente a necessidade, uma alternativa e como consultar o
custo. Não estime o saldo da minha conta nem prometa um custo fixo por vídeo.
```

### Briefing de edição (skill bônus 1)
```text
Leia e aplique a skill meia-briefing-de-edicao. Use briefing/[NOME].md e os materiais
deste projeto para preparar o briefing desta edição. Resolva as lacunas relevantes sem
repetir perguntas já respondidas. Se faltar algo essencial, identifique exatamente o que
falta. Meu vídeo é originais/[ARQUIVO] e o resultado desejado é [OBJETIVO].
```

### Usar uma referência
```text
Use [ARQUIVO OU LINK DA REFERÊNCIA] para entender [TIPOGRAFIA, RITMO OU ENQUADRAMENTO].
Aplique esses critérios ao nosso material e à nossa identidade. Não copie textos,
ofertas ou elementos de marca da referência. Antes de executar, resuma quais
características serão aproveitadas.
```

### Conferir o briefing antes de executar
```text
Confira o briefing e os arquivos deste projeto. Liste o vídeo original, os materiais de
apoio disponíveis e qualquer informação que falte para executar o pedido. Se um arquivo
estiver ausente ou ambíguo, identifique o problema. Não invente materiais nem dados da
oferta e não inicie a edição até resolvermos essas lacunas.
```

---

## 2 · Editar a base (aula 5)

### Criar a edição simples (amostra de 8 s)
```text
Edite originais/[ARQUIVO] para 1080 × 1920 criando projeto/src/edicoes/[NOME]-V01-simples.ts
a partir de _modelo.ts. Transcreva a fala real com npm run transcrever e revise os termos
[NOMES E TERMOS]. Preserve a voz e o sentido da fala. Centralize o apresentador sem cortar
partes importantes do rosto ou da cabeça. Use legendas simples de até duas linhas, com
contraste, sem cobrir o rosto e com margem para a interface da plataforma. Identifique
pausas e erros de gravação; não corte automaticamente trechos que mudem o sentido. Nesta
versão, não acrescente música, imagens ou motion. Primeiro gere a amostra de 8 segundos
([NOME]-V01-simples-amostra) e informe como abrir a prévia. Aguarde minha aprovação.
+ BLOCO TÉCNICO
```

### Legendas e enquadramento (skill bônus 2)
```text
Leia e aplique a skill meia-legendas-e-enquadramento. Ajuste as legendas e o
enquadramento de [EDIÇÃO] para [FORMATO E DESTINO], preservando a voz, o sentido e o
estilo já aprovado. Confira uma amostra representativa com áudio e informe qual
intervalo foi realmente verificado.
```

### Corrigir somente o trecho
```text
Na amostra, entre [INÍCIO-FIM], corrija [PROBLEMA] desta forma: [MUDANÇA DESEJADA].
Preserve a fala, o áudio, a identidade e todos os pontos já aprovados. Gere novamente
apenas o trecho alterado e suas transições para eu conferir.
```

### Concluir a base
```text
A amostra está aprovada. Aplique esse padrão ao restante do vídeo. Revise a transcrição,
principalmente [NOMES E TERMOS OU NENHUM TERMO ESPECIAL]. Preserve a voz, o sentido da
fala e as decisões já aprovadas. Mantenha a versão [NOME]-V01-simples, o projeto editável
e o original. Abra a prévia completa ([NOME]-V01-simples-completo) para minha revisão.
```

---

## 3 · Inserções e motion (aulas 6–7)

### Adicionar imagens pela fala
```text
Crie [NOME]-V02-insercoes.ts como cópia da V01 aprovada. Use somente os arquivos de
projeto/public/assets. Sincronize as inserções pela fala real, sem assumir tempos fixos:
1. "[FRASE 1]": apresente assets/[ARQUIVO 1] em [ÁREA].
2. "[FRASE 2]": apresente assets/[ARQUIVO 2] em [ÁREA].
Preserve o conteúdo e a proporção das imagens. Mantenha o rosto visível e centralizado e
as legendas longe da borda inferior. Use entradas discretas e uma inserção principal por
vez. Primeiro apresente uma prévia dos trechos alterados. Aguarde minha revisão antes de
exportar. Não acrescente números, promessas ou dados que não estejam na gravação.
```

### Moldura e motion explicativo
```text
Na [NOME]-V02, quando a fala disser "[FRASE QUE ABRE A EXPLICAÇÃO]", leve o apresentador
para a moldura (canto inferior direito, ~42% × 34%) e use o quadro livre para explicar
[CONCEITO] com [ÍCONES / CARTÕES / FLUXO] animados pela fala. Volte à tela cheia em
"[FRASE QUE ENCERRA]". Destaque só o item em discussão e reduza a ênfase dos demais.
Mantenha o rosto centralizado na moldura e a legenda em faixa livre. Gere uma amostra de
10 a 15 segundos com a transição para a moldura. Aguarde minha aprovação.
+ BLOCO TÉCNICO
```

### Se precisar corrigir o enquadramento na moldura
```text
No trecho [INÍCIO-FIM], o rosto está [PROBLEMA]. Ajuste somente a posição e o tamanho
do vídeo dentro da moldura (enquadramento) para centralizar o apresentador e preservar a
cabeça e os gestos importantes. Mantenha cartões, duração, legenda e áudio aprovados.
Mostre a transição para a moldura e a prévia do trecho corrigido.
```

---

## 4 · Variações A/B/C (instrução extra)

```text
Use uma cópia da edição aprovada, que será a versão A ([CAMPANHA]-A-base). Na cópia,
substitua somente o título da abertura entre [INÍCIO-FIM] por "[NOVO TÍTULO]". Preserve
voz, corpo do vídeo, oferta, provas e CTA. Salve como [CAMPANHA]-B-titulo e apresente a
prévia da abertura. Não altere a versão A.
```
```text
Crie outra cópia da versão A aprovada e substitua apenas a fala de abertura pelo take
originais/[ARQUIVO DO NOVO TAKE]. Ajuste a transição e a legenda desse trecho. Preserve o
corpo do vídeo, a oferta e o CTA. Salve como [CAMPANHA]-C-nova-fala e apresente a prévia
da abertura. Não sobrescreva A nem B.
```
```text
Organize as versões A, B e C sem sobrescrever projetos nem originais. Preencha
fichas/matriz-de-variacoes.csv com versão, arquivo, variável alterada, destino [CANAL] e
hipótese [O QUE QUERO TESTAR]. Não invente métricas ou resultados.
```

---

## 5 · Aula horizontal 16:9 (aula 9)

```text
Use a skill remotion-best-practices para editar originais/[ARQUIVO DA AULA] em formato
horizontal 16:9 (formato: 'horizontal'). Se a skill não estiver disponível, informe antes
de afirmar que a utilizou. Preserve o original.
É uma aula. Faça cortes nas pausas excessivas e nos erros, mas mantenha respirações
naturais e o tempo necessário para entender a explicação. Não acelere como um anúncio.
Use o apresentador em tela cheia como base. Quando um conceito precisar de apoio visual,
coloque-o na moldura à direita e abra um quadro branco à esquerda, com motions
explicativos sincronizados à fala (ícones, blocos, fluxos, textos curtos). Volte à tela
cheia ao terminar a explicação. Transcreva o vídeo real; use [ROTEIRO] só como referência
e preserve improvisos corretos. Apresente uma prévia para revisão.
```

---

## 6 · Fluxo do Claude Code (aula extra)

### Pedido 1 · cortes
```text
Verifique se a skill remotion-best-practices está disponível e use as orientações
relevantes para editar originais/[VÍDEO]. Remova erros, tentativas abandonadas e
repetições; quando houver mais de uma execução da mesma fala, mantenha a de melhor
performance e continuidade. Encurte pausas excessivas sem deixar a fala artificial. Use
[ROTEIRO] como referência, sem inventar falas ou cortar algo que mude o sentido. Nesta
primeira versão, faça apenas os cortes e apresente a prévia para eu aprovar.
```

### Pedido 2 · edição visual
```text
Os cortes estão aprovados. Use a mesma base e as orientações da skill Remotion para
adicionar transições, textos animados e ícones que expliquem os conceitos nos momentos
correspondentes da fala. Use os logos oficiais de projeto/public/assets quando as marcas
forem citadas; se faltar um arquivo, sinalize. Quando a explicação precisar de espaço,
use a moldura com o rosto centralizado e o quadro ao lado. Preserve cortes, voz e
conteúdo aprovados. Abra a prévia para revisão.
```

### Ajustar só o brilho necessário
```text
Entre [INÍCIO-FIM], o apresentador está escuro. Ajuste moderadamente o brilho apenas da
camada do apresentador, preservando o tom de pele e os detalhes nas áreas claras. Mantenha
cortes, textos, logos, cores e motions aprovados. Mostre uma comparação antes e depois.
```

---

## 7 · Revisar sem refazer (skill bônus 3)

### Revisão econômica
```text
Leia e aplique a skill meia-revisao-economia. Revise [EDIÇÃO] para corrigir [PROBLEMA] no
intervalo [INÍCIO-FIM]. Preserve os pontos aprovados. Use o histórico das tentativas, se
houver, para identificar a causa antes de repetir alterações e confira o trecho corrigido
com suas transições. Não estime consumo ou custos sem dados.
```

### Revisão objetiva (lista única)
```text
Ajuste somente estes pontos:
1. [INÍCIO-FIM]: [PROBLEMA] → [MUDANÇA DESEJADA].
2. [INÍCIO-FIM]: [PROBLEMA] → [MUDANÇA DESEJADA].
3. [INÍCIO-FIM]: [PROBLEMA] → [MUDANÇA DESEJADA].
Preserve voz, duração, identidade, dados verificados e trechos aprovados. Não reconstrua
o projeto nem abra uma nova direção criativa. Gere prévias apenas das partes alteradas,
com alguns segundos antes e depois. Aguarde minha revisão antes de exportar.
```

### Se o mesmo erro se repetir
```text
O mesmo problema ocorreu novamente: [DESCREVA]. Antes de tentar outra alteração,
identifique a causa e proponha a menor correção possível. Preserve o restante da edição e
teste apenas o trecho [INÍCIO-FIM]. Não refaça o vídeo inteiro para corrigir esse ponto.
```

### Verificação final
```text
Confira a versão final: fala e oferta preservadas, legenda correta, áudio inteligível,
rosto visível, assets sem cortes indevidos, CTA legível e duração correta. Aponte qualquer
problema concreto com o tempo correspondente. Não acrescente efeitos ou novas ideias.
```

---

## 8 · Exportar e reutilizar (instrução extra)

### Exportar o aprovado
```text
A edição completa está aprovada. Exporte [ID]-completo em MP4 H.264 com áudio AAC,
na resolução do formato, preservando duração e taxa de quadros aprovadas. Salve em
entregas/[NOME]-final.mp4, sem sobrescrever originais nem entregas anteriores. Abra o
arquivo e confira áudio, sincronização das legendas, enquadramento e leitura do CTA.
```

### Guardar o padrão aprovado
```text
Documente em padrao/padrao-visual.md as regras aprovadas de fonte, cores, legenda,
margens, enquadramento, moldura, transições, inserções e exportação, e alinhe
projeto/src/tema.ts. Separe as regras reutilizáveis das informações específicas deste
vídeo. Atualize o checklist curto para o próximo vídeo.
```

### Adaptar o próximo vídeo
```text
Crie uma nova edição a partir da aprovada para originais/[NOVO ARQUIVO]. Preserve a
edição anterior e os originais. Use as regras de padrao/padrao-visual.md. Refaça a
transcrição e adapte as inserções à nova fala usando [ASSETS DESTE VÍDEO]. A oferta é
[OFERTA] e o CTA é [CTA]. Não reutilize informações específicas do vídeo anterior.
Primeiro apresente uma amostra de 8 segundos.
```

### Lote pequeno (só depois de aprovar a adaptação)
```text
Tenho três vídeos: [ARQUIVOS]. Use o padrão visual aprovado, mas adapte transcrição,
títulos, inserções e CTA ao conteúdo de cada um. Comece somente pelo primeiro e apresente
uma amostra. Depois da minha aprovação, prossiga com os demais. Registre as versões e
qualquer material ausente. Não use serviços pagos adicionais sem autorização.
```

### Registrar o esforço de produção
```text
Registre em fichas/controle-de-custos.csv: data [DATA], versão [VERSÃO], assinaturas
alocadas [VALOR], uso adicional [VALOR], API [VALOR], extras [VALOR], tempo ativo
[MINUTOS], espera [MINUTOS], peças aprovadas [QUANTIDADE]. Use apenas os dados que
forneci; preserve registros anteriores; calcule o custo por peça só se houver peças
aprovadas e todos os valores.
```
