import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {cores, fontes} from '../tema';

// Aula 2: composição vertical de 5 segundos para confirmar que o ambiente funciona.
export const TesteInicial: React.FC = () => {
	const frame = useCurrentFrame();
	const entrada = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});

	return (
		<AbsoluteFill style={{backgroundColor: cores.fundo, justifyContent: 'center', alignItems: 'center'}}>
			<div
				style={{
					fontFamily: fontes.titulo,
					fontWeight: 700,
					fontSize: 110,
					lineHeight: 1.05,
					color: cores.texto,
					textAlign: 'center',
					opacity: entrada,
					transform: `translateY(${(1 - entrada) * 40}px)`,
				}}
			>
				Meu primeiro
				<br />
				projeto
			</div>
		</AbsoluteFill>
	);
};
