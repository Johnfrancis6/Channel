import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');

// Sur une machine sans acces au telechargement du navigateur de Remotion
// (ex. sandbox de developpement), definir REMOTION_BROWSER_EXECUTABLE pour
// reutiliser un Chromium/Chrome deja installe. En production (poste de
// Franco), laisser Remotion telecharger le sien normalement.
if (process.env.REMOTION_BROWSER_EXECUTABLE) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE);
}
