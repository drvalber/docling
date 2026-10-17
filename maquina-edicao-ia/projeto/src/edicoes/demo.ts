import type {Edicao} from '../tipos';

// DEMONSTRAÇÃO sem gravação: mostra o padrão (legenda, título, moldura, inserção
// e CTA) antes de você ter um vídeo. O texto é o roteiro de exercício da aula 5 e
// os tempos são ESTIMADOS. Em uma edição real, as legendas vêm da transcrição da
// fala gravada (npm run transcrever), nunca do roteiro.
export const demo: Edicao = {
	id: 'demo',
	formato: 'vertical',
	fps: 30,
	video: null,
	duracaoSegundos: 25,
	amostra: {inicio: 3, fim: 11},
	enquadramento: {focoX: 50, focoY: 35, zoom: 1},
	moldura: [{inicio: 5.2, fim: 15}],
	legendas: [
		{inicio: 0, fim: 2.4, texto: 'Se toda semana você começa'},
		{inicio: 2.4, fim: 3.6, texto: 'seu conteúdo do zero,'},
		{inicio: 3.6, fim: 5.2, texto: 'escolha um assunto que seus clientes sempre perguntam.'},
		{inicio: 5.2, fim: 7.4, texto: 'Grave uma resposta curta, mostre um exemplo'},
		{inicio: 7.4, fim: 9.8, texto: 'e termine com um próximo passo claro.'},
		{inicio: 9.8, fim: 12.4, texto: 'Com uma estrutura aprovada,'},
		{inicio: 12.4, fim: 15, texto: 'você pode produzir novos vídeos'},
		{inicio: 15, fim: 16.6, texto: 'sem decidir fonte, legenda'},
		{inicio: 16.6, fim: 18.2, texto: 'e enquadramento outra vez.'},
		{inicio: 18.2, fim: 21.4, texto: 'Na aula aberta, eu mostro como organizar esse processo.'},
		{inicio: 21.4, fim: 25, texto: 'Toque em Saiba Mais para conhecer.'},
	],
	titulos: [{inicio: 0.3, fim: 4.9, texto: 'Conteúdo do zero?'}],
	insercoes: [{inicio: 5.6, fim: 14.8, arquivo: 'assets/demo-estrutura.svg', area: 'quadro-livre'}],
	cta: {inicio: 18.2, fim: 25, titulo: 'AULA ABERTA', apoio: 'Toque em Saiba Mais'},
	demonstracao: true,
};
