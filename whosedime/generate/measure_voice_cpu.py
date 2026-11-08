"""Real-time factor of the voice notebook's own code on this machine's CPU (S11).

    pip install --index-url https://download.pytorch.org/whl/cpu torch torchaudio
    pip install qwen-tts faster-whisper pyloudnorm librosa
    python3 whosedime/generate/measure_voice_cpu.py OUT_DIR

Designs a narrator (VoiceDesign, description A, the reference text), clones it on the Base
model for a 57-word sample, transcribes it with Whisper, and prints the times. Measured in
S11 on 4 CPU cores, 15 GB: design x5.0, clone x6.1 real time, similarity 1.0
(docs/whosedime/generation_report.md). Downloads about 9 GB of models the first time.
"""
import json, sys, time, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "notebooks"))
import numpy as np
import voice_whosedime as vw
S = vw.load_settings()
out = sys.argv[1] if len(sys.argv) > 1 else "voice_cpu_measure"
res = {"threads": __import__("torch").get_num_threads()}
TEXT = ("In 2008, two friends could not find a taxi on a snowy night in Paris. "
        "One of them had an idea: tap a button, and a black car comes to you. "
        "It sounded simple. It was not cheap. Somebody had to pay for every ride, "
        "and for years, it was not the person in the back seat.")
res["words"] = len(TEXT.split())
t = time.time(); designer = vw.qwen_designer(S, device="cpu"); res["load_design_s"] = round(time.time() - t, 1)
t = time.time(); a, sr = designer(S["design"]["reference_text"], S["design"]["descriptions"]["A"], S["seed"])
res["design_s"] = round(time.time() - t, 1); res["design_audio_s"] = round(len(a) / sr, 2)
os.makedirs(out + "/Voice", exist_ok=True)
vw.write_wav(out + "/Voice/ref.wav", a, sr)
open(out + "/Voice/ref.txt", "w").write(S["design"]["reference_text"])
del designer; import gc; gc.collect()
print(json.dumps(res), flush=True)
t = time.time(); synth = vw.qwen_clone_synth(out + "/Voice", S, device="cpu"); res["load_base_s"] = round(time.time() - t, 1)
t = time.time(); b, sr2 = synth(TEXT, S["seed"]); res["clone_s"] = round(time.time() - t, 1)
res["clone_audio_s"] = round(len(b) / sr2, 2); vw.write_wav(out + "/sample50.wav", b, sr2)
res["rtf_clone"] = round(res["clone_s"] / res["clone_audio_s"], 2)
print(json.dumps(res), flush=True)
t = time.time(); al = vw.whisper_aligner(S); words = al(b, sr2, TEXT); res["whisper_s"] = round(time.time() - t, 1)
res["similarity"] = round(vw.similarity(TEXT, " ".join(w["word"] for w in words)), 3)
print(json.dumps(res), flush=True)
json.dump(res, open(out + "/measure.json", "w"), indent=1)
