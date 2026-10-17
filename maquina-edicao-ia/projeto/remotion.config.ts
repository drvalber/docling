import {Config} from '@remotion/cli/config';

// Saída padrão do curso: MP4 H.264 com áudio AAC.
Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
Config.setOverwriteOutput(false);
