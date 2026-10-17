import React from 'react';
import {Composition} from 'remotion';
import {EdicaoVideo, calcularMetadados, type EdicaoVideoProps} from './composicoes/EdicaoVideo';
import {TesteInicial} from './composicoes/TesteInicial';
import {edicoes} from './edicoes';
import {carregarFontes} from './fontes';
import {layouts} from './tema';

carregarFontes();

export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="TesteInicial" component={TesteInicial} durationInFrames={150} fps={30} width={1080} height={1920} />
		{edicoes.flatMap((edicao) =>
			(['amostra', 'completo'] as const).map((trecho) => {
				const layout = layouts[edicao.formato];
				const props: EdicaoVideoProps = {edicao, trecho};
				return (
					<Composition
						key={`${edicao.id}-${trecho}`}
						id={`${edicao.id}-${trecho}`}
						component={EdicaoVideo}
						defaultProps={props}
						calculateMetadata={calcularMetadados}
						durationInFrames={1}
						fps={edicao.fps}
						width={layout.largura}
						height={layout.altura}
					/>
				);
			}),
		)}
	</>
);
