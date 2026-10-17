#!/usr/bin/env node
// Transcreve a fala REAL de um vídeo com Whisper.cpp, localmente e sem serviço pago,
// e gera blocos de legenda (até ~2 linhas) no formato usado por src/edicoes.
//
// Uso:
//   npm run transcrever -- --video public/originais/aula.mp4 --saida src/edicoes/aula.legendas.json
//   Opções: --modelo small|medium|large-v3-turbo (padrão: small) --idioma pt
//
// Na primeira execução, instala o Whisper.cpp e baixa o modelo em ./whisper
// (centenas de MB; precisa de internet uma única vez). Depois roda offline.
// Revise SEMPRE o resultado: nomes, termos técnicos, números e acentos.

import {execFileSync} from 'node:child_process';
import {writeFileSync} from 'node:fs';
import path from 'node:path';
import {downloadWhisperModel, installWhisperCpp, toCaptions, transcribe} from '@remotion/install-whisper-cpp';

const VERSAO_WHISPER = '1.5.5';
const MAX_CARACTERES = 42; // ~2 linhas de legenda vertical
const PAUSA_QUEBRA_MS = 450;

const lerArgs = () => {
	const args = process.argv.slice(2);
	const opcoes = {modelo: 'small', idioma: 'pt'};
	for (let i = 0; i < args.length; i += 2) {
		const chave = args[i].replace(/^--/, '');
		opcoes[chave] = args[i + 1];
	}
	if (!opcoes.video || !opcoes.saida) {
		console.error('Informe --video <arquivo> e --saida <arquivo.json>.');
		process.exit(1);
	}
	return opcoes;
};

// Agrupa palavras em unidades de sentido (pontuação ou pausa longa) e divide
// unidades longas em partes equilibradas, sem deixar palavras órfãs.
const agruparEmBlocos = (captions) => {
	const palavras = captions
		.map((c) => ({texto: c.text.trim(), inicioMs: c.startMs, fimMs: c.endMs}))
		.filter((p) => p.texto);

	const unidades = [];
	let atual = [];
	palavras.forEach((p, i) => {
		atual.push(p);
		const proxima = palavras[i + 1];
		const pausa = proxima ? proxima.inicioMs - p.fimMs : 0;
		if (!proxima || /[.,!?;:]$/.test(p.texto) || pausa > PAUSA_QUEBRA_MS) {
			unidades.push(atual);
			atual = [];
		}
	});

	const tamanho = (ps) => ps.map((p) => p.texto).join(' ').length;
	const blocos = [];
	for (const unidade of unidades) {
		const partes = Math.ceil(tamanho(unidade) / MAX_CARACTERES);
		const alvo = tamanho(unidade) / partes;
		let bloco = [];
		for (const p of unidade) {
			if (bloco.length && tamanho([...bloco, p]) > alvo + 6) {
				blocos.push(bloco);
				bloco = [];
			}
			bloco.push(p);
		}
		blocos.push(bloco);
	}

	return blocos.map((ps) => ({
		inicio: Number((ps[0].inicioMs / 1000).toFixed(2)),
		fim: Number((ps[ps.length - 1].fimMs / 1000).toFixed(2)),
		texto: ps.map((p) => p.texto).join(' '),
	}));
};

const main = async () => {
	const {video, saida, modelo, idioma} = lerArgs();
	// O instalador cria a pasta; se ela existir sem o executável, ele pede para apagá-la.
	const pastaWhisper = path.resolve('whisper');
	await installWhisperCpp({to: pastaWhisper, version: VERSAO_WHISPER});
	await downloadWhisperModel({model: modelo, folder: pastaWhisper});

	// Whisper precisa de WAV 16 kHz mono; usa o ffmpeg que acompanha o Remotion.
	const wav = path.join(pastaWhisper, 'audio-16k.wav');
	execFileSync('npx', ['remotion', 'ffmpeg', '-y', '-i', video, '-ar', '16000', '-ac', '1', wav], {stdio: 'inherit'});

	const resultado = await transcribe({
		inputPath: wav,
		whisperPath: pastaWhisper,
		whisperCppVersion: VERSAO_WHISPER,
		model: modelo,
		tokenLevelTimestamps: true,
		language: idioma,
	});
	const {captions} = toCaptions({whisperCppOutput: resultado});
	const legendas = agruparEmBlocos(captions);

	writeFileSync(saida, JSON.stringify(legendas, null, '\t') + '\n');
	console.log(`${legendas.length} blocos de legenda salvos em ${saida}. Revise antes de usar.`);
};

main().catch((erro) => {
	console.error(erro);
	process.exit(1);
});
