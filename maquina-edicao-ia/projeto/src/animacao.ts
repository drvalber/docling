import {Easing, interpolate} from 'remotion';
import type {Intervalo} from './tipos';

// Toda animação deriva do frame da composição (nada de CSS animations ou relógio
// próprio), para a prévia e o MP4 exportado terem exatamente o mesmo movimento.

export const segParaFrame = (segundos: number, fps: number) => Math.round(segundos * fps);

export const ativo = (frame: number, fps: number, intervalo: Intervalo) =>
	frame >= segParaFrame(intervalo.inicio, fps) && frame < segParaFrame(intervalo.fim, fps);

// 0 → 1 na entrada, 1 → 0 na saída. Fora do intervalo, 0.
export const presenca = (frame: number, fps: number, intervalo: Intervalo, transicaoSeg = 0.35) => {
	const inicio = segParaFrame(intervalo.inicio, fps);
	const fim = segParaFrame(intervalo.fim, fps);
	const t = Math.max(1, Math.min(segParaFrame(transicaoSeg, fps), Math.floor((fim - inicio) / 2)));
	return interpolate(frame, [inicio, inicio + t, fim - t, fim], [0, 1, 1, 0], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
		easing: Easing.inOut(Easing.cubic),
	});
};

// Maior presença entre vários intervalos (ex.: todos os trechos em moldura).
export const presencaEmAlgum = (frame: number, fps: number, intervalos: Intervalo[], transicaoSeg?: number) =>
	intervalos.reduce((max, i) => Math.max(max, presenca(frame, fps, i, transicaoSeg)), 0);

export const misturar = (a: number, b: number, p: number) => a + (b - a) * p;
