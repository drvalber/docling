// Contrato de dados de uma edição. Cada vídeo tem um arquivo em src/edicoes/
// que descreve O QUE entra e QUANDO; os componentes decidem COMO aparece.
// Todos os tempos estão em segundos da gravação original.

export type Intervalo = {
	inicio: number;
	fim: number;
};

export type Legenda = Intervalo & {
	texto: string;
};

export type Titulo = Intervalo & {
	texto: string;
};

export type AreaInsercao = 'acima-da-cabeca' | 'quadro-livre';

export type Insercao = Intervalo & {
	// Caminho dentro de projeto/public (ex.: "assets/grafico.png").
	arquivo: string;
	area: AreaInsercao;
	// Texto curto opcional sob a imagem (ex.: aviso de ilustração didática).
	rotulo?: string;
};

export type Cta = Intervalo & {
	titulo: string;
	apoio?: string;
};

export type Enquadramento = {
	// Ponto do rosto na gravação, em % (0-100). Mantém o rosto centralizado
	// quando o vídeo é recortado para tela cheia ou para a moldura.
	focoX: number;
	focoY: number;
	// 1 = sem zoom. Use valores pequenos (1.0-1.3) para não perder nitidez.
	zoom: number;
};

export type Formato = 'vertical' | 'horizontal';

export type Edicao = {
	id: string;
	formato: Formato;
	fps: number;
	// Caminho dentro de projeto/public (ex.: "originais/aula-01.mp4") ou null
	// para uma demonstração sem gravação.
	video: string | null;
	// Usado somente quando não há vídeo; com vídeo, a duração vem do arquivo.
	duracaoSegundos: number;
	// Trecho representativo de ~8 s para aprovar o padrão antes do vídeo inteiro.
	amostra: Intervalo;
	enquadramento: Enquadramento;
	// Intervalos em que o apresentador vai para a moldura e libera espaço.
	moldura: Intervalo[];
	legendas: Legenda[];
	titulos: Titulo[];
	insercoes: Insercao[];
	cta: Cta | null;
	// Marca a edição como demonstração: exibe um aviso na tela.
	demonstracao: boolean;
};
