import {Config} from '@remotion/cli/config';

// Frames en PNG, pas en JPEG.
//
// Le CRF par defaut du h264 est 18 (@remotion/renderer/dist/crf.js) : l'etape
// d'encodage est quasi transparente. La seule perte de la chaine etait donc
// **avant** elle — chaque frame ecrasee en JPEG a la qualite par defaut de 80
// (DEFAULT_JPEG_QUALITY), puis encodee presque sans perte. Sur un fond
// #0B0F14 avec degrades, ca fabrique des paliers et des blocs dans les noirs.
//
// Le cout est un rendu plus lent : l'encodage PNG de chaque frame est plus
// cher que le JPEG. Si le temps de rendu devient genant sur le poste de
// Franco, revenir a 'jpeg' en montant explicitement la qualite :
//   Config.setVideoImageFormat('jpeg'); Config.setJpegQuality(100);
Config.setVideoImageFormat('png');

// Sur une machine sans acces au telechargement du navigateur de Remotion
// (ex. sandbox de developpement), definir REMOTION_BROWSER_EXECUTABLE pour
// reutiliser un Chromium/Chrome deja installe. En production (poste de
// Franco), laisser Remotion telecharger le sien normalement.
if (process.env.REMOTION_BROWSER_EXECUTABLE) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE);
}
