import type {Formato} from './tipos';

// Padrão visual reutilizável. Altere aqui (e registre em padrao/padrao-visual.md)
// em vez de espalhar cores e tamanhos pelos componentes.
export const cores = {
	fundo: '#0d0a1a',
	fundoGrade: 'rgba(167, 139, 250, 0.07)',
	destaque: '#a78bfa', // lilás
	apoio: '#22d3ee', // ciano
	texto: '#f5f3ff',
	textoEscuro: '#140f24',
	legendaFundo: 'rgba(13, 10, 26, 0.78)',
	borda: 'rgba(245, 243, 255, 0.35)',
	aviso: '#fbbf24',
};

export const fontes = {
	titulo: 'Sora',
	texto: 'Manrope',
};

export type Retangulo = {x: number; y: number; w: number; h: number};

type Layout = {
	largura: number;
	altura: number;
	// Moldura do apresentador quando ele libera espaço para explicações.
	moldura: Retangulo;
	raioMoldura: number;
	// Área livre para imagens e motions enquanto a moldura está ativa.
	quadroLivre: Retangulo;
	// Faixa acima da cabeça para banner, títulos e CTA.
	acimaDaCabeca: Retangulo;
	legenda: {
		// Distância da borda inferior: margem para a interface da plataforma.
		margemInferior: number;
		larguraMaxima: number;
		tamanho: number;
	};
	titulo: {tamanho: number};
};

export const layouts: Record<Formato, Layout> = {
	// 1080 × 1920 (9:16). Moldura no canto inferior direito, ~42% × 34% (aula 7).
	vertical: {
		largura: 1080,
		altura: 1920,
		moldura: {x: 578, y: 1180, w: 454, h: 653},
		raioMoldura: 36,
		quadroLivre: {x: 48, y: 190, w: 984, h: 770},
		acimaDaCabeca: {x: 60, y: 150, w: 960, h: 420},
		legenda: {margemInferior: 400, larguraMaxima: 960, tamanho: 58},
		titulo: {tamanho: 88},
	},
	// 1920 × 1080 (16:9). Moldura à direita e quadro à esquerda (aula 9).
	horizontal: {
		largura: 1920,
		altura: 1080,
		moldura: {x: 1290, y: 110, w: 570, h: 800},
		raioMoldura: 32,
		quadroLivre: {x: 70, y: 110, w: 1160, h: 800},
		acimaDaCabeca: {x: 360, y: 60, w: 1200, h: 260},
		legenda: {margemInferior: 70, larguraMaxima: 1500, tamanho: 50},
		titulo: {tamanho: 72},
	},
};
