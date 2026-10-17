import type {Edicao} from '../tipos';

// MODELO para uma edição real. Copie este arquivo para src/edicoes/<nome>.ts,
// troque o nome da constante e registre-a em src/edicoes/index.ts.
//
// 1. Copie a gravação de originais/ para public/originais/ (o original fica preservado).
// 2. Rode: npm run transcrever -- --video public/originais/<arquivo>.mp4 --saida src/edicoes/<nome>.legendas.json
// 3. Revise o JSON gerado (nomes, termos técnicos, acentos) antes de usar.
// 4. Ajuste o enquadramento pelo rosto e defina a amostra de ~8 s.
//
// import legendas from './<nome>.legendas.json';

export const modelo: Edicao = {
	id: 'modelo',
	formato: 'vertical',
	fps: 30,
	video: 'originais/SEU-VIDEO.mp4',
	duracaoSegundos: 0, // ignorado quando há vídeo
	amostra: {inicio: 0, fim: 8},
	enquadramento: {focoX: 50, focoY: 35, zoom: 1},
	moldura: [],
	legendas: [], // legendas (do JSON revisado)
	titulos: [],
	insercoes: [],
	cta: null, // use apenas um CTA real
	demonstracao: false,
};
