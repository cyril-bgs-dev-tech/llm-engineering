#!/usr/bin/env python3
"""Export ONNX et quantification INT8 statique de l'encodeur déployable (RM-44, fiche 2026-10-05-onnx-int8-statique), développement seulement, pli 0.

Variantes : PyTorch 32 bits (référence mesurée dans le même script), ONNX 32 bits, INT8 statique QDQ sur les multiplications matricielles (étalonnage MinMax, puis centiles, puis centiles sans la tête
ni la dernière couche). Étalonnage sur 128 textes des plis d'entraînement du modèle, sans étiquette. Dépendances ONNX hors verrou : `artifacts/spikes/onnx_pkgs`, ajouté en fin de `sys.path`.
Usage : onnx_int8_static.py SLUG_DU_MODELE [--threads 8] [--register]"""
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.append(str(ROOT / "artifacts/spikes/onnx_pkgs"))
import onnx
import onnxruntime as ort
from onnxruntime.quantization import CalibrationDataReader, CalibrationMethod, QuantFormat, QuantType, quantize_static
from onnxruntime.quantization.shape_inference import quant_pre_process
from transformers import AutoModelForSequenceClassification, AutoTokenizer

import p1_04_06_tfidf
import p1_finetune
from llmft import evaluation
from llmft.mini_registry import register_run

N_CALIBRATION = 128
WORK = ROOT / "artifacts/spikes/onnx_work"


class Reader(CalibrationDataReader):  # type: ignore[misc]
    def __init__(self, sequences: list[list[int]]) -> None:
        self.items = iter(sequences)

    def get_next(self) -> dict[str, np.ndarray] | None:
        ids = next(self.items, None)
        if ids is None:
            return None
        return {"input_ids": np.array([ids], dtype=np.int64), "attention_mask": np.ones((1, len(ids)), dtype=np.int64)}


def softmax(z: np.ndarray) -> np.ndarray:
    e = np.exp(z - z.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def evaluate_session(run: Any, sequences: list[list[int]], truth: np.ndarray, labels: list[str], excluded: str) -> dict[str, float]:
    logits, lat = [], []
    for ids in sequences:
        s = time.perf_counter()
        logits.append(run(ids))
        lat.append(1000 * (time.perf_counter() - s))
    rep = evaluation.chapter_report(truth, softmax(np.vstack(logits)), labels, excluded=(excluded,))
    return {"macro_f1": round(rep["macro_f1"], 4), "latence_ms_p50": round(float(np.percentile(lat[5:], 50)), 1), "latence_ms_p95": round(float(np.percentile(lat[5:], 95)), 1)}


def main() -> int:
    slug = sys.argv[1]
    threads = int(sys.argv[sys.argv.index("--threads") + 1]) if "--threads" in sys.argv else 8
    torch.set_num_threads(threads)
    WORK.mkdir(parents=True, exist_ok=True)
    model_dir = ROOT / "artifacts/models" / slug
    texts, y, folds, excluded, _ = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    te = np.where(folds == 0)[0]
    tr = np.where(folds != 0)[0]
    tok = AutoTokenizer.from_pretrained(model_dir)
    x = p1_finetune.build_inputs(tok, [texts[i] for i in te], 508)
    rng = np.random.default_rng(20261005)
    calib = p1_finetune.build_inputs(tok, [texts[i] for i in rng.choice(tr, N_CALIBRATION, replace=False)], 508)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir, torch_dtype=torch.float32).eval()
    results: dict[str, Any] = {}

    def torch_run(ids: list[int]) -> np.ndarray:
        t = torch.tensor([ids])
        with torch.no_grad():
            return model(input_ids=t, attention_mask=torch.ones_like(t)).logits.numpy()

    results["pytorch_fp32"] = evaluate_session(torch_run, x, idx[te], labels, excluded)
    print("pytorch_fp32", results["pytorch_fp32"], flush=True)

    fp32 = WORK / "encoder_fp32.onnx"
    d = torch.tensor([[5, 6, 7, 8, 9, 10, 11, 12], [5, 6, 7, 8, 9, 10, 11, 12]])
    torch.onnx.export(model, (d, torch.ones_like(d)), str(fp32), input_names=["input_ids", "attention_mask"], output_names=["logits"], opset_version=17, dynamo=False,
                      dynamic_axes={"input_ids": {0: "batch", 1: "seq"}, "attention_mask": {0: "batch", 1: "seq"}, "logits": {0: "batch"}})
    pre = WORK / "encoder_pre.onnx"
    quant_pre_process(str(fp32), str(pre), skip_symbolic_shape=True)
    options = ort.SessionOptions()
    options.intra_op_num_threads = threads

    def ort_runner(path: Path) -> Any:
        sess = ort.InferenceSession(str(path), options, providers=["CPUExecutionProvider"])
        return lambda ids: sess.run(None, {"input_ids": np.array([ids], dtype=np.int64), "attention_mask": np.ones((1, len(ids)), dtype=np.int64)})[0]

    results["onnx_fp32"] = {**evaluate_session(ort_runner(fp32), x, idx[te], labels, excluded), "taille_mo": round(fp32.stat().st_size / 1e6, 1)}
    print("onnx_fp32", results["onnx_fp32"], flush=True)

    matmul_names = [n.name for n in onnx.load(str(pre)).graph.node if n.op_type == "MatMul"]
    keep_float = [n for n in matmul_names if "classifier" in n or "layer.11" in n]
    specs = {
        "int8_statique_minmax": (CalibrationMethod.MinMax, []),
        "int8_statique_centiles": (CalibrationMethod.Percentile, []),
        "int8_statique_centiles_sans_tete_ni_derniere_couche": (CalibrationMethod.Percentile, keep_float),
    }
    for name, (method, excluded_nodes) in specs.items():
        out = WORK / f"encoder_{name}.onnx"
        quantize_static(str(pre), str(out), Reader(calib), quant_format=QuantFormat.QDQ, activation_type=QuantType.QInt8, weight_type=QuantType.QInt8, per_channel=True,
                        op_types_to_quantize=["MatMul"], nodes_to_exclude=excluded_nodes, calibrate_method=method)
        results[name] = {**evaluate_session(ort_runner(out), x, idx[te], labels, excluded), "taille_mo": round(out.stat().st_size / 1e6, 1), "noeuds_exclus": len(excluded_nodes)}
        print(name, results[name], flush=True)
    ref = results["pytorch_fp32"]
    for name, r in results.items():
        r["macro_f1_moins_pytorch_points"] = round(100 * (r["macro_f1"] - ref["macro_f1"]), 2)
        r["latence_p50_relative_a_pytorch"] = round(r["latence_ms_p50"] / ref["latence_ms_p50"], 3)
        r["retenue"] = bool(name.startswith("int8") and r["macro_f1_moins_pytorch_points"] > -1.0 and r["latence_p50_relative_a_pytorch"] <= 0.70)
    out_all = {"modele": slug, "threads": threads, "n_patients_pli0": len(x), "n_etalonnage": N_CALIBRATION, "onnxruntime": ort.__version__, **results}
    (ROOT / "results/measures" / f"onnx_int8_static_{slug}.json").write_text(json.dumps(out_all, indent=1), encoding="utf-8")
    if "--register" in sys.argv:
        kept = [k for k, v in results.items() if v["retenue"]]
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": f"onnx-int8-statique-{slug}", "status": "ok", "summary": f"ONNX et INT8 statique de {slug} : retenues {kept or 'aucune'}",
                                                    "params": {"threads": threads, "n_calibration": N_CALIBRATION}, "metrics": out_all}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
