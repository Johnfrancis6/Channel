"""
Le schema schemas/state_schema.json n'etait utilise par aucun code ni aucun
test : rien ne garantissait que ce que l'Orchestrateur et les agents ecrivent
correspond encore au contrat documente (§5.4).

Ces tests le branchent sur les etats reellement produits par le pipeline.

Lancer : python3 -m pytest tests/test_schema_state.py -v
"""

import json
import os
import shutil
import tempfile
import unittest

from orchestrateur.constants import ORDRE_IDS
from orchestrateur.main import run_once
from orchestrateur.state_store import load_state, save_state

from tests.test_orchestrateur_factice import _valider_checkpoint

jsonschema = None
try:
    import jsonschema as _jsonschema
    jsonschema = _jsonschema
except ImportError:  # pragma: no cover
    pass

RACINE_DEPOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(RACINE_DEPOT, "schemas", "state_schema.json")
TEMPLATE_PATH = os.path.join(RACINE_DEPOT, "skills", "new-short", "assets", "state_template.json")


def _charger(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestSchemaEtPipeline(unittest.TestCase):
    """Verifications structurelles, sans dependance externe."""

    def test_le_schema_couvre_exactement_les_etapes_du_pipeline(self):
        """Garde-fou contre une etape ajoutee dans constants.PIPELINE mais
        oubliee dans le schema (ou l'inverse) : `etapes` est en
        additionalProperties:false, donc l'oubli rendrait tout state invalide."""
        etapes_schema = set(_charger(SCHEMA_PATH)["properties"]["etapes"]["properties"])
        self.assertEqual(etapes_schema, set(ORDRE_IDS))

    def test_le_template_couvre_exactement_les_etapes_du_pipeline(self):
        self.assertEqual(set(_charger(TEMPLATE_PATH)["etapes"]), set(ORDRE_IDS))

    def test_le_template_deploye_est_identique_a_la_source(self):
        """.claude/skills/ est une copie de skills/ : elle doit suivre."""
        deploye = os.path.join(RACINE_DEPOT, ".claude", "skills", "new-short",
                               "assets", "state_template.json")
        if not os.path.isfile(deploye):
            self.skipTest(".claude/skills/new-short non deploye")
        self.assertEqual(_charger(deploye), _charger(TEMPLATE_PATH))


@unittest.skipIf(jsonschema is None, "jsonschema non installe")
class TestValidationSchema(unittest.TestCase):
    def setUp(self):
        self.schema = _charger(SCHEMA_PATH)
        self.root = tempfile.mkdtemp(prefix="chaine_yt_schema_")
        os.makedirs(os.path.join(self.root, "videos"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _valider(self, state, contexte):
        try:
            jsonschema.validate(state, self.schema)
        except jsonschema.ValidationError as e:
            self.fail(f"{contexte} : {e.message} (chemin : {list(e.absolute_path)})")

    def _creer_video_depuis_template(self, video_id):
        video_dir = os.path.join(self.root, "videos", video_id)
        os.makedirs(os.path.join(video_dir, "checkpoints"), exist_ok=True)
        state = _charger(TEMPLATE_PATH)
        state.update(video_id=video_id, cree_le="2026-09-10T07:00:00Z",
                     titre_travail="Titre de test", pilier="actu_ia", voie="rapide")
        save_state(video_dir, state)
        return video_dir

    def test_le_template_est_valide(self):
        self._valider(_charger(TEMPLATE_PATH), "state_template.json")

    def test_etat_valide_a_chaque_etape_du_parcours_nominal(self):
        video_dir = self._creer_video_depuis_template("2026-09-10_v01")

        run_once(self.root)
        self._valider(load_state(video_dir), "apres E1 / ouverture CP1")

        _valider_checkpoint(video_dir, "CP1")
        run_once(self.root)
        self._valider(load_state(video_dir), "apres CP1 valide")

        _valider_checkpoint(video_dir, "CP2")
        run_once(self.root)
        self._valider(load_state(video_dir), "apres CP2 valide (E4 parallele E5)")

        state = load_state(video_dir)
        state["etapes"]["E4_audio"]["statut"] = "termine"
        save_state(video_dir, state)
        run_once(self.root)
        self._valider(load_state(video_dir), "apres montage / ouverture CP3")

        _valider_checkpoint(video_dir, "CP3")
        run_once(self.root)
        self._valider(load_state(video_dir), "apres CP3 valide")

    def test_etat_valide_apres_un_refus(self):
        video_dir = self._creer_video_depuis_template("2026-09-10_v02")
        run_once(self.root)
        _valider_checkpoint(video_dir, "CP1", statut="REFUSE", commentaire="Angle trop vague")
        run_once(self.root)
        self._valider(load_state(video_dir), "apres refus au CP1")

    def test_etat_valide_apres_une_alerte(self):
        video_dir = self._creer_video_depuis_template("2026-09-10_v03")
        state = load_state(video_dir)
        state["_scenario"] = {"E1_recherche": "echec"}
        save_state(video_dir, state)
        for _ in range(3):
            run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["E1_recherche"]["statut"], "alerte")
        state.pop("_scenario")
        self._valider(state, "apres 3 echecs / alerte")


if __name__ == "__main__":
    unittest.main()


class TestGrapheDeDependances(unittest.TestCase):
    """
    Le graphe vivait a deux endroits : `depend_de` dans constants.PIPELINE,
    que personne ne lisait, et un dictionnaire ecrit a la main dans
    engine.py. Ils concordaient ; rien ne l'imposait. Meme motif que la
    geometrie des composants — deux constantes liees qui vivent separement.
    """

    # Le graphe attendu, ecrit une fois ici pour epingler la derivation.
    ATTENDU = {
        "E1_recherche": [],
        "CP1": ["E1_recherche"],
        "E2_redaction": ["CP1"],
        "E3_filtre": ["E2_redaction"],
        "CP2": ["E3_filtre"],
        "E4_audio": ["CP2"],
        "E5_storyboard": ["CP2"],
        "E6_montage": ["E4_audio", "E5_storyboard"],
        "CP3": ["E6_montage"],
        "E7_publication": ["CP3"],
    }

    def test_le_graphe_derive_est_celui_attendu(self):
        from orchestrateur.constants import DEPENDANCES
        self.assertEqual(DEPENDANCES, self.ATTENDU)

    def test_engine_ne_redeclare_pas_le_graphe(self):
        from orchestrateur import constants, engine
        self.assertIs(engine.DEPENDANCES, constants.DEPENDANCES)

    def test_chaque_prealable_existe_et_precede(self):
        from orchestrateur.constants import DEPENDANCES, ORDRE_IDS
        for etape, prealables in DEPENDANCES.items():
            for prealable in prealables:
                self.assertIn(prealable, ORDRE_IDS, f"{etape} depend de {prealable}, inconnu")
                self.assertLess(ORDRE_IDS.index(prealable), ORDRE_IDS.index(etape),
                                f"{etape} depend de {prealable}, qui vient apres")

    def test_le_parallelisme_du_cp2_est_declare_explicitement(self):
        # E5 ne depend pas de E4 : les deux partent du CP2. Sans `depend_de`,
        # la derivation par position les mettrait en serie.
        from orchestrateur.constants import PIPELINE_PAR_ID
        self.assertEqual(PIPELINE_PAR_ID["E5_storyboard"]["depend_de"], ["CP2"])
        self.assertEqual(PIPELINE_PAR_ID["E6_montage"]["depend_de"],
                         ["E4_audio", "E5_storyboard"])
