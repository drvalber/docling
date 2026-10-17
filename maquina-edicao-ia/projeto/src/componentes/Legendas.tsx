import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {ativo, misturar, presencaEmAlgum, segParaFrame} from '../animacao';
import {cores, fontes, layouts} from '../tema';
import type {Edicao} from '../tipos';

// Legenda simples, até duas linhas, com contraste e margem acima da interface
// da plataforma. Quando o apresentador vai para a moldura, a faixa sobe para
// não cobrir o rosto.
export const Legendas: React.FC<{edicao: Edicao}> = ({edicao}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const layout = layouts[edicao.formato];
	const atual = edicao.legendas.find((l) => ativo(frame, fps, l));
	if (!atual) {
		return null;
	}

	const p = presencaEmAlgum(frame, fps, edicao.moldura, 0.6);
	const margemComMoldura = edicao.formato === 'vertical'
		? layout.altura - layout.moldura.y + 20
		: layout.legenda.margemInferior;
	const margem = misturar(layout.legenda.margemInferior, margemComMoldura, p);

	const entrada = interpolate(frame - segParaFrame(atual.inicio, fps), [0, 4], [0, 1], {
		extrapolateRight: 'clamp',
	});

	return (
		<div
			style={{
				position: 'absolute',
				left: 0,
				right: 0,
				bottom: margem,
				display: 'flex',
				justifyContent: 'center',
				opacity: entrada,
				transform: `translateY(${(1 - entrada) * 12}px)`,
			}}
		>
			<div
				style={{
					maxWidth: layout.legenda.larguraMaxima,
					padding: '14px 28px',
					borderRadius: 18,
					background: cores.legendaFundo,
					color: cores.texto,
					fontFamily: fontes.texto,
					fontWeight: 700,
					fontSize: layout.legenda.tamanho,
					lineHeight: 1.22,
					textAlign: 'center',
					// Nunca esconder palavras: blocos com mais de duas linhas devem ser
					// divididos na edição (o script de transcrição já faz isso).
				}}
			>
				{atual.texto}
			</div>
		</div>
	);
};
