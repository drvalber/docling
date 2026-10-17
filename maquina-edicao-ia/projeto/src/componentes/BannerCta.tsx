import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {segParaFrame} from '../animacao';
import {cores, fontes, layouts} from '../tema';
import type {Edicao} from '../tipos';

// Convite final acima da cabeça. Entra uma vez e permanece até o fim do
// intervalo, para garantir tempo de leitura (não desaparece num efeito).
export const BannerCta: React.FC<{edicao: Edicao}> = ({edicao}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const {cta} = edicao;
	if (!cta) {
		return null;
	}
	const inicio = segParaFrame(cta.inicio, fps);
	const fim = segParaFrame(cta.fim, fps);
	if (frame < inicio || frame >= fim) {
		return null;
	}
	const layout = layouts[edicao.formato];
	const area = layout.acimaDaCabeca;
	const p = interpolate(frame - inicio, [0, segParaFrame(0.4, fps)], [0, 1], {extrapolateRight: 'clamp'});

	return (
		<div
			style={{
				position: 'absolute',
				left: area.x,
				top: area.y,
				width: area.w,
				display: 'flex',
				justifyContent: 'center',
				opacity: p,
				transform: `translateY(${(1 - p) * -30}px)`,
			}}
		>
			<div
				style={{
					padding: '28px 44px',
					borderRadius: 28,
					background: `linear-gradient(135deg, ${cores.destaque}, ${cores.apoio})`,
					color: cores.textoEscuro,
					textAlign: 'center',
					boxShadow: '0 24px 60px rgba(0,0,0,0.5)',
				}}
			>
				<div style={{fontFamily: fontes.titulo, fontWeight: 700, fontSize: layout.titulo.tamanho * 0.9}}>
					{cta.titulo}
				</div>
				{cta.apoio ? (
					<div style={{fontFamily: fontes.texto, fontWeight: 700, fontSize: layout.legenda.tamanho * 0.8, marginTop: 8}}>
						{cta.apoio}
					</div>
				) : null}
			</div>
		</div>
	);
};
