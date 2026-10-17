import {parseMedia} from '@remotion/media-parser';
import React from 'react';
import {AbsoluteFill, type CalculateMetadataFunction, Sequence, staticFile} from 'remotion';
import {segParaFrame} from '../animacao';
import {Apresentador} from '../componentes/Apresentador';
import {BannerCta} from '../componentes/BannerCta';
import {Insercoes} from '../componentes/Insercoes';
import {Legendas} from '../componentes/Legendas';
import {Titulos} from '../componentes/Titulos';
import {cores, fontes, layouts} from '../tema';
import type {Edicao} from '../tipos';

export type Trecho = 'completo' | 'amostra';

export type EdicaoVideoProps = {
	edicao: Edicao;
	trecho: Trecho;
};

const Fundo: React.FC = () => (
	<AbsoluteFill
		style={{
			backgroundColor: cores.fundo,
			backgroundImage: `linear-gradient(${cores.fundoGrade} 1px, transparent 1px), linear-gradient(90deg, ${cores.fundoGrade} 1px, transparent 1px)`,
			backgroundSize: '60px 60px',
		}}
	/>
);

const AvisoDemonstracao: React.FC = () => (
	<div
		style={{
			position: 'absolute',
			top: 40,
			left: 40,
			padding: '8px 18px',
			borderRadius: 10,
			background: 'rgba(0,0,0,0.6)',
			color: cores.aviso,
			fontFamily: fontes.texto,
			fontWeight: 700,
			fontSize: 26,
		}}
	>
		DEMONSTRAÇÃO · sem gravação · tempos estimados
	</div>
);

// Camadas, de trás para frente: fundo, apresentador, inserções, títulos, CTA, legenda.
const Camadas: React.FC<{edicao: Edicao}> = ({edicao}) => (
	<AbsoluteFill>
		<Fundo />
		<Apresentador edicao={edicao} />
		<Insercoes edicao={edicao} />
		<Titulos edicao={edicao} />
		<BannerCta edicao={edicao} />
		<Legendas edicao={edicao} />
		{edicao.demonstracao ? <AvisoDemonstracao /> : null}
	</AbsoluteFill>
);

export const EdicaoVideo: React.FC<EdicaoVideoProps> = ({edicao, trecho}) => {
	if (trecho === 'completo') {
		return <Camadas edicao={edicao} />;
	}
	// A amostra reproduz exatamente o mesmo trecho da edição completa.
	return (
		<Sequence from={-segParaFrame(edicao.amostra.inicio, edicao.fps)}>
			<Camadas edicao={edicao} />
		</Sequence>
	);
};

export const calcularMetadados: CalculateMetadataFunction<EdicaoVideoProps> = async ({props}) => {
	const {edicao, trecho} = props;
	const layout = layouts[edicao.formato];
	let duracao = edicao.duracaoSegundos;
	if (edicao.video) {
		const {slowDurationInSeconds} = await parseMedia({
			src: staticFile(edicao.video),
			fields: {slowDurationInSeconds: true},
			acknowledgeRemotionLicense: true,
		});
		duracao = slowDurationInSeconds;
	}
	const segundos = trecho === 'amostra' ? Math.min(edicao.amostra.fim, duracao) - edicao.amostra.inicio : duracao;
	return {
		durationInFrames: Math.max(1, segParaFrame(segundos, edicao.fps)),
		fps: edicao.fps,
		width: layout.largura,
		height: layout.altura,
	};
};
