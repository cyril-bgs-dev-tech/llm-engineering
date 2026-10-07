#!/usr/bin/env python3
"""Service d'un seul tenant du système final G, de l'ensemble E et de la cascade (fiche 2026-10-07-service-bout-en-bout-g ; RM-35, RM-48). Développement seulement, texte seul, jamais le test scellé.
Usage : bench_service_g.py {gpu|cpu} [--n 200] [--register] ; à lancer sous scripts/run_guarded.sh, GPU libre pour le mode gpu.
Mode gpu : LoRA fusionné bf16, cinq encodeurs bf16, TF-IDF ; deux passages complets, essai à quatre clients, accord bf16 contre fp32. Mode cpu : cinq encodeurs fp32 et TF-IDF sur processeur, huit fils."""
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

T_PROCESS = time.perf_counter()

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import os

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_HOME", str(ROOT / "artifacts/hf_cache"))
import p1_04_06_tfidf
from llmft import lora_train, servicecost, tokenizer_guard
from llmft import service_g as sg
from llmft.energy import PowerSampler, read_gpu_power_w
from llmft.mini_registry import register_run

FINAL = ROOT / "artifacts/final"
ENC_SEEDS = (1000, 1001, 1002, 1003, 1004)
SHARE_FIRST_STAGE = 0.934  # part traitée par l'étage encodeurs : cascade hors pli, run 20261005-030146-cascade-cinq-plis-encodeur-lora


def arg(name: str, default: str) -> str:
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


class Service:
    """Composants chargés une fois ; `predict_one` rend les probabilités par composante et le temps de chaque étage."""

    def __init__(self, mode: str, labels: list[str]) -> None:
        import joblib
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.torch, self.mode, self.labels = torch, mode, labels
        self.device = "cuda" if mode == "gpu" else "cpu"
        dtype = torch.bfloat16 if mode == "gpu" else torch.float32
        d = joblib.load(FINAL / "tfidf.joblib")
        self.vec, self.tfidf = d["vec"], d["model"]
        self.enc_tok = AutoTokenizer.from_pretrained(FINAL / "final-encoder-s1000")
        self.encoders = [AutoModelForSequenceClassification.from_pretrained(FINAL / f"final-encoder-s{s}", torch_dtype=dtype).to(self.device).eval() for s in ENC_SEEDS]
        self.lora: Any = None
        if mode == "gpu":
            from peft import PeftModel

            self.lora_tok = AutoTokenizer.from_pretrained("Qwen/Qwen3.5-4B")
            self.pad_id = self.lora_tok.pad_token_id if self.lora_tok.pad_token_id is not None else self.lora_tok.eos_token_id
            base = AutoModelForSequenceClassification.from_pretrained("Qwen/Qwen3.5-4B", num_labels=len(labels), torch_dtype=torch.bfloat16)
            base.config.pad_token_id = self.pad_id
            if hasattr(base.config, "text_config"):
                base.config.text_config.pad_token_id = self.pad_id
            self.lora = PeftModel.from_pretrained(base, FINAL / "final-lora-s1000").merge_and_unload().to("cuda").eval()

    def _forward(self, model: Any, ids: list[int], pad_id: int) -> np.ndarray:
        x, m = lora_train._pad([ids], pad_id, self.device)
        with self.torch.no_grad():
            return self.torch.softmax(model(input_ids=x, attention_mask=m).logits.float(), dim=-1).cpu().numpy()

    def predict_one(self, text: str, with_lora: bool = True) -> tuple[dict[str, np.ndarray], dict[str, float]]:
        ms: dict[str, float] = {}
        t = time.perf_counter()
        ids = tokenizer_guard.build_inputs_local(self.enc_tok, [text], 508)[0]
        ms["tokenisation_encodeur"] = 1000 * (time.perf_counter() - t)
        t = time.perf_counter()
        enc = [self._forward(m, ids, self.enc_tok.pad_token_id) for m in self.encoders]
        ms["cinq_encodeurs"] = 1000 * (time.perf_counter() - t)
        t = time.perf_counter()
        tf = self._tfidf(text)
        ms["tfidf"] = 1000 * (time.perf_counter() - t)
        out: dict[str, np.ndarray] = {"encodeurs": np.stack(enc), "tfidf": tf}
        if with_lora and self.lora is not None:
            t = time.perf_counter()
            lids = tokenizer_guard.build_inputs_local(self.lora_tok, [text], 4096)[0]
            ms["tokenisation_lora"] = 1000 * (time.perf_counter() - t)
            t = time.perf_counter()
            out["lora"] = self._forward(self.lora, lids, self.pad_id)
            ms["lora"] = 1000 * (time.perf_counter() - t)
        t = time.perf_counter()
        if "lora" in out:
            out["g"] = sg.combine_g(out["lora"], list(out["encodeurs"]), tf)
        ms["combinaison"] = 1000 * (time.perf_counter() - t)
        return out, ms

    def _tfidf(self, text: str) -> np.ndarray:
        from llmft import tfidf

        return tfidf.predict_aligned(self.vec, self.tfidf, [text], self.labels)


def run_pass(svc: Service, sample: list[str], price: float) -> dict[str, Any]:
    """Un passage complet en lot de 1 ; l'énergie n'est lue que sur GPU (la carte ne mesure pas le processeur)."""
    totals: list[float] = []
    stages: dict[str, list[float]] = {}
    classes: list[int] = []
    with PowerSampler(reader=read_gpu_power_w if svc.mode == "gpu" else lambda: None) as ps:
        for text in sample:
            t = time.perf_counter()
            out, ms = svc.predict_one(text)
            totals.append(1000 * (time.perf_counter() - t))
            for k, v in ms.items():
                stages.setdefault(k, []).append(v)
            probs = out["g"] if "g" in out else 0.5 * out["encodeurs"].mean(0) + 0.5 * out["tfidf"]  # sur processeur : E
            classes.append(int(probs.argmax()))
    e = servicecost.energy_wh(np.array(ps.samples), 1.0) if ps.samples else 0.0
    return {"total": sg.latency_percentiles(totals), "etages_p50_ms": {k: round(float(np.percentile(v, 50)), 2) for k, v in stages.items()},
            "energie": servicecost.per_1000(e, len(sample), price) if ps.samples else None, "classes": classes}


def concurrent_test(svc: Service, sample: list[str], clients: int = 4) -> dict[str, Any]:
    lock = threading.Lock()
    lat: list[float] = []

    def one(text: str) -> None:
        t = time.perf_counter()
        with lock:
            svc.predict_one(text)
        lat.append(1000 * (time.perf_counter() - t))

    t0 = time.perf_counter()
    with ThreadPoolExecutor(clients) as pool:
        list(pool.map(one, sample))
    wall = time.perf_counter() - t0
    return {"clients": clients, "requetes": len(sample), "debit_patients_par_s": round(len(sample) / wall, 2), **sg.latency_percentiles(lat)}


def precision_agreement(svc: Service, sample: list[str]) -> dict[str, float]:
    """Accord des classes prédites entre encodeurs bf16 (service) et fp32 (entraînement) : encodeurs moyennés seuls, puis G."""
    from transformers import AutoModelForSequenceClassification

    fp32 = [AutoModelForSequenceClassification.from_pretrained(FINAL / f"final-encoder-s{s}", torch_dtype=svc.torch.float32).to("cuda").eval() for s in ENC_SEEDS]
    agree_enc = agree_g = 0
    for text in sample:
        out, _ = svc.predict_one(text)
        ids = tokenizer_guard.build_inputs_local(svc.enc_tok, [text], 508)[0]
        enc32 = [svc._forward(m, ids, svc.enc_tok.pad_token_id) for m in fp32]
        agree_enc += int(out["encodeurs"].mean(0).argmax() == np.mean(enc32, axis=0).argmax())
        agree_g += int(out["g"].argmax() == sg.combine_g(out["lora"], enc32, out["tfidf"]).argmax())
    return {"encodeurs_moyennes": round(agree_enc / len(sample), 4), "g": round(agree_g / len(sample), 4)}


def main() -> int:
    mode = sys.argv[1]
    n, price = int(arg("--n", "200")), float(arg("--price-eur-kwh", "0.25"))
    import torch

    if mode == "cpu":
        torch.set_num_threads(8)
    texts, y, folds, _, _ = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    sample = [t for t, g in zip(texts, folds, strict=True) if g == 0][:n]
    svc = Service(mode, labels)
    ready_s = time.perf_counter() - T_PROCESS
    t = time.perf_counter()
    svc.predict_one(sample[0])
    first_ms = 1000 * (time.perf_counter() - t)
    for text in sample[1:4]:
        svc.predict_one(text)  # échauffement
    if mode == "gpu":
        torch.cuda.reset_peak_memory_stats()
    passes = [run_pass(svc, sample, price) for _ in range(2)]
    peak = round(torch.cuda.max_memory_allocated() / 2**30, 2) if mode == "gpu" else None
    out: dict[str, Any] = {"mode": mode, "n_patients": len(sample), "demarrage_a_froid_s": round(ready_s, 1), "premiere_requete_ms": round(first_ms, 1), "memoire_pic_gib": peak,
                           "passages": [{k: v for k, v in p.items() if k != "classes"} for p in passes],
                           "classes_identiques_entre_passages": passes[0]["classes"] == passes[1]["classes"],
                           "passages_acceptes": sg.passes_accepted(passes[0]["total"]["p50_ms"], passes[1]["total"]["p50_ms"], same_classes=passes[0]["classes"] == passes[1]["classes"]),
                           "prix_eur_kwh_parametre": price}
    st = passes[0]["etages_p50_ms"]
    first = st["tokenisation_encodeur"] + st["cinq_encodeurs"]
    out["modele_ensemble_E_ms"] = round(first + st["tfidf"], 1)
    if mode == "gpu":
        second = st["tokenisation_lora"] + st["lora"]
        out["modele_cascade_encodeurs_puis_lora_ms"] = round(sg.cascade_mean_latency(first, second, SHARE_FIRST_STAGE), 1)
        out["part_premier_etage_hors_pli"] = SHARE_FIRST_STAGE
        out["essai_concurrent"] = concurrent_test(svc, sample)
        out["accord_bf16_fp32"] = precision_agreement(svc, sample)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    (ROOT / "results/measures" / f"service_g_{mode}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": f"service-g-bout-en-bout-{mode}", "status": "ok", "summary": f"Service d'un seul tenant, mode {mode} : p50 {passes[0]['total']['p50_ms']} ms, p95 {passes[0]['total']['p95_ms']} ms",
                                                    "params": {"fiche": "experiments/2026-10-07-service-bout-en-bout-g.md", "n": len(sample), "mode": mode}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
