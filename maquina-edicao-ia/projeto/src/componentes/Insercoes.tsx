import React from 'react';
import {Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {presenca} from '../animacao';
import {cores, fontes, layouts} from '../tema';
import type {Edicao} from '../tipos';

// Imagens de apoio sincronizadas à fala. Preserva proporção e conteúdo (contain),
// com entrada discreta e uma inserção principal por vez.
export const Insercoes: React.FC<{edicao: Edicao}> = ({edicao}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const layout = layouts[edicao.formato];

	return (
		<>
			{edicao.insercoes.map((ins) => {
				const p = presenca(frame, fps, ins, 0.35);
				if (p === 0) {
					return null;
				}
				const area = ins.area === 'acima-da-cabeca' ? layout.acimaDaCabeca : layout.quadroLivre;
				return (
					<div
						key={`${ins.inicio}-${ins.arquivo}`}
						style={{
							position: 'absolute',
							left: area.x,
							top: area.y,
							width: area.w,
							height: area.h,
							display: 'flex',
							flexDirection: 'column',
							alignItems: 'center',
							justifyContent: 'center',
							gap: 16,
							opacity: p,
							transform: `translateY(${(1 - p) * 24}px) scale(${0.94 + 0.06 * p})`,
						}}
					>
						<Img
							src={staticFile(ins.arquivo)}
							style={{
								maxWidth: '100%',
								maxHeight: ins.rotulo ? '86%' : '100%',
								objectFit: 'contain',
								borderRadius: 20,
								boxShadow: '0 20px 50px rgba(0,0,0,0.45)',
							}}
						/>
						{ins.rotulo ? (
							<div style={{fontFamily: fontes.texto, fontSize: 28, color: cores.aviso}}>{ins.rotulo}</div>
						) : null}
					</div>
				);
			})}
		</>
	);
};
