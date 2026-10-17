import type {Edicao} from '../tipos';
import {demo} from './demo';

// Cada edição registrada aqui gera duas composições no Studio:
// <id>-amostra (trecho de aprovação) e <id>-completo (vídeo inteiro).
// Para versões (ex.: V01-simples, V02-insercoes), crie um arquivo por versão
// e preserve as anteriores.
export const edicoes: Edicao[] = [demo];
