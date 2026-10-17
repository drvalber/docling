import React from 'react';
import {AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {misturar, presencaEmAlgum} from '../animacao';
import {cores, fontes, layouts} from '../tema';
import type {Edicao} from '../tipos';

// Apresentador em tela cheia que vai para a moldura nos intervalos indicados.
// O recorte usa o ponto de foco do rosto, então ele continua centralizado nos dois estados.
export const Apresentador: React.FC<{edicao: Edicao}> = ({edicao}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const layout = layouts[edicao.formato];
	const p = presencaEmAlgum(frame, fps, edicao.moldura, 0.6);

	const {moldura} = layout;
	const x = misturar(0, moldura.x, p);
	const y = misturar(0, moldura.y, p);
	const w = misturar(layout.largura, moldura.w, p);
	const h = misturar(layout.altura, moldura.h, p);
	const raio = misturar(0, layout.raioMoldura, p);
	const {focoX, focoY, zoom} = edicao.enquadramento;

	const midia = edicao.video ? (
		<OffthreadVideo
			src={staticFile(edicao.video)}
			style={{
				width: '100%',
				height: '100%',
				objectFit: 'cover',
				objectPosition: `${focoX}% ${focoY}%`,
				transform: `scale(${zoom})`,
				transformOrigin: `${focoX}% ${focoY}%`,
			}}
		/>
	) : (
		<AbsoluteFill
			style={{
				background: `linear-gradient(160deg, #2a2145, #120e22)`,
				justifyContent: 'center',
				alignItems: 'center',
				color: cores.borda,
				fontFamily: fontes.titulo,
				fontSize: 44,
				letterSpacing: 6,
			}}
		>
			APRESENTADOR
		</AbsoluteFill>
	);

	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: y,
				width: w,
				height: h,
				borderRadius: raio,
				overflow: 'hidden',
				border: p > 0 ? `${2 * p}px solid ${cores.borda}` : undefined,
				boxShadow: p > 0 ? `0 ${24 * p}px ${60 * p}px rgba(0,0,0,${0.45 * p})` : undefined,
			}}
		>
			{midia}
		</div>
	);
};
