import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {presenca} from '../animacao';
import {cores, fontes, layouts} from '../tema';
import type {Edicao} from '../tipos';

// Título curto que destaca uma ideia. Não repete a legenda inteira.
export const Titulos: React.FC<{edicao: Edicao}> = ({edicao}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const layout = layouts[edicao.formato];
	const area = layout.acimaDaCabeca;

	return (
		<>
			{edicao.titulos.map((t) => {
				const p = presenca(frame, fps, t, 0.3);
				if (p === 0) {
					return null;
				}
				return (
					<div
						key={`${t.inicio}-${t.texto}`}
						style={{
							position: 'absolute',
							left: area.x,
							top: area.y,
							width: area.w,
							display: 'flex',
							justifyContent: 'center',
							opacity: p,
							transform: `translateY(${(1 - p) * 30}px) scale(${0.96 + 0.04 * p})`,
						}}
					>
						<div
							style={{
								fontFamily: fontes.titulo,
								fontWeight: 700,
								fontSize: layout.titulo.tamanho,
								lineHeight: 1.05,
								color: cores.texto,
								textAlign: 'center',
								textTransform: 'uppercase',
								letterSpacing: -1,
								textShadow: '0 6px 30px rgba(0,0,0,0.55)',
							}}
						>
							{t.texto}
							<div
								style={{
									height: 8,
									marginTop: 14,
									borderRadius: 4,
									background: `linear-gradient(90deg, ${cores.destaque}, ${cores.apoio})`,
									transform: `scaleX(${p})`,
								}}
							/>
						</div>
					</div>
				);
			})}
		</>
	);
};
