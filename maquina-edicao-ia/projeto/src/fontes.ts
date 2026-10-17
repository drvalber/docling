import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';
import {fontes} from './tema';

// Fontes locais (licença OFL em public/fontes): a renderização não depende da internet.
export const carregarFontes = () =>
	Promise.all([
		loadFont({family: fontes.titulo, url: staticFile('fontes/sora-700.ttf'), weight: '700'}),
		loadFont({family: fontes.texto, url: staticFile('fontes/manrope-400.ttf'), weight: '400'}),
		loadFont({family: fontes.texto, url: staticFile('fontes/manrope-700.ttf'), weight: '700'}),
	]);
