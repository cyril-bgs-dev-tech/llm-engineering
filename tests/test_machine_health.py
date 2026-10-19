from llmft import machine_health

DMESG = """[    0.000000] Linux version 6.6.114.1-microsoft-standard-WSL2
[ 4511.120339] python3.12[88123]: segfault at 0 ip 0000000000000000 sp 00007ffd error 14 in python3.12[400000+1000]
[ 4600.000001] hv_balloon: something unrelated
[ 4602.523001] tokenizers[90001]: segfault at 7f00 ip 00007f12 sp 00007ffd error 4 in libtokenizers.so
"""


def snap(boot: str = "b45e9baf", segv: int | None = 0, uptime: float = 100.0) -> machine_health.Snapshot:
    return machine_health.Snapshot(boot_id=boot, kernel_segfaults=segv, uptime_s=uptime)


def test_le_journal_du_noyau_compte_les_lignes_de_segfault_seulement():
    assert machine_health.count_kernel_segfaults(DMESG) == 2


def test_un_journal_vide_compte_zero_segfault():
    assert machine_health.count_kernel_segfaults("") == 0


def test_meme_demarrage_sans_nouveau_segfault_donne_ok():
    verdict = machine_health.verdict(snap(segv=3), snap(segv=3, uptime=900.0))
    assert verdict.status == "ok"
    assert verdict.reasons == ()


def test_un_segfault_du_noyau_pendant_le_calcul_rend_le_run_suspect():
    verdict = machine_health.verdict(snap(segv=3), snap(segv=4, uptime=900.0))
    assert verdict.status == "suspect"
    assert "1 segfault" in verdict.reasons[0]


def test_un_redemarrage_pendant_le_calcul_rend_le_run_suspect():
    verdict = machine_health.verdict(snap(boot="aaaa"), snap(boot="bbbb"))
    assert verdict.status == "suspect"
    assert any("démarrage" in r for r in verdict.reasons)


def test_un_temps_de_fonctionnement_qui_recule_signale_un_redemarrage_meme_sans_identifiant():
    verdict = machine_health.verdict(snap(uptime=5000.0), snap(uptime=20.0))
    assert verdict.status == "suspect"


def test_un_journal_du_noyau_illisible_ne_donne_jamais_ok():
    verdict = machine_health.verdict(snap(segv=None), snap(segv=None))
    assert verdict.status == "inconnu"
    assert "illisible" in verdict.reasons[0]


def test_le_tampon_contient_debut_fin_et_verdict_serialisables():
    stamp = machine_health.stamp(snap(segv=0), end=snap(segv=0, uptime=200.0))
    assert stamp["verdict"] == "ok"
    assert stamp["start"]["boot_id"] == "b45e9baf"
    assert stamp["end"]["uptime_s"] == 200.0
    assert stamp["reasons"] == []


def test_la_photo_lit_les_sources_fournies():
    s = machine_health.snapshot(read_boot_id=lambda: "abc\n", read_uptime=lambda: "123.45 999.0\n", read_dmesg=lambda: DMESG)
    assert s == machine_health.Snapshot(boot_id="abc", kernel_segfaults=2, uptime_s=123.45)


def test_la_photo_survit_a_un_journal_du_noyau_inaccessible():
    def refuse() -> str:
        raise PermissionError("dmesg: read kernel buffer failed")

    s = machine_health.snapshot(read_boot_id=lambda: "abc", read_uptime=lambda: "1.0 1.0", read_dmesg=refuse)
    assert s.kernel_segfaults is None


def run(created: str, status: str = "ok", health: dict | None = None, **extra) -> dict:
    record = {"run_id": f"{created[:10]}-x", "created_at": created, "status": status, **extra}
    if health is not None:
        record["machine_health"] = health
    return record


def test_un_run_ancien_sans_tampon_n_est_pas_signale():
    assert machine_health.unhealthy_runs([run("2026-10-07T12:00:00Z")], since="2026-10-17T00:00:00Z") == []


def test_un_run_recent_sans_tampon_est_signale():
    out = machine_health.unhealthy_runs([run("2026-10-17T01:00:00Z")], since="2026-10-17T00:00:00Z")
    assert out == [("2026-10-17-x", "sans tampon de santé de la machine")]


def test_un_run_recent_suspect_est_signale_avec_ses_raisons():
    health = {"verdict": "suspect", "reasons": ["1 segfault(s) du noyau pendant le calcul"]}
    out = machine_health.unhealthy_runs([run("2026-10-18T01:00:00Z", health=health)], since="2026-10-17T00:00:00Z")
    assert out == [("2026-10-18-x", "verdict suspect : 1 segfault(s) du noyau pendant le calcul")]


def test_un_run_recent_sain_passe():
    health = {"verdict": "ok", "reasons": []}
    assert machine_health.unhealthy_runs([run("2026-10-18T01:00:00Z", health=health)], since="2026-10-17T00:00:00Z") == []


def test_un_run_en_echec_ou_interrompu_n_a_pas_besoin_de_tampon():
    runs = [run("2026-10-18T01:00:00Z", status="failed"), run("2026-10-18T02:00:00Z", status="aborted")]
    assert machine_health.unhealthy_runs(runs, since="2026-10-17T00:00:00Z") == []


def test_une_derogation_ecrite_laisse_passer_un_run_suspect():
    health = {"verdict": "suspect", "reasons": ["1 segfault(s)"]}
    runs = [run("2026-10-18T01:00:00Z", health=health, health_waiver="calcul refait deux fois, empreintes identiques (agree_twice)")]
    assert machine_health.unhealthy_runs(runs, since="2026-10-17T00:00:00Z") == []


def test_une_derogation_vide_ne_compte_pas():
    runs = [run("2026-10-18T01:00:00Z", health_waiver="  ")]
    assert len(machine_health.unhealthy_runs(runs, since="2026-10-17T00:00:00Z")) == 1


def test_un_run_sans_tampon_remplace_par_un_run_sain_qui_le_cite_n_est_plus_signale():
    """Convention du registre : une correction est un nouveau run qui cite l'ancien dans `supersedes` (incident du 17/10 : frontière enregistrée sans tampon)."""
    old = {"run_id": "20261017-030144-frontiere", "created_at": "2026-10-17T03:01:44Z", "status": "ok"}
    new = {"run_id": "20261017-031000-frontiere", "created_at": "2026-10-17T03:10:00Z", "status": "ok", "supersedes": "20261017-030144-frontiere", "machine_health": {"verdict": "ok", "reasons": []}}
    assert machine_health.unhealthy_runs([old, new], since="2026-10-17T00:00:00Z") == []


def test_un_remplacant_lui_meme_sans_tampon_ne_couvre_pas_l_ancien():
    old = {"run_id": "a-1", "created_at": "2026-10-17T03:01:44Z", "status": "ok"}
    new = {"run_id": "a-2", "created_at": "2026-10-17T03:10:00Z", "status": "ok", "supersedes": "a-1"}
    assert sorted(r for r, _ in machine_health.unhealthy_runs([old, new], since="2026-10-17T00:00:00Z")) == ["a-1", "a-2"]


def test_un_remplacant_suspect_ne_couvre_pas_l_ancien():
    old = {"run_id": "b-1", "created_at": "2026-10-17T03:01:44Z", "status": "ok"}
    new = {"run_id": "b-2", "created_at": "2026-10-17T03:10:00Z", "status": "ok", "supersedes": "b-1", "machine_health": {"verdict": "suspect", "reasons": ["1 segfault(s)"]}}
    assert sorted(r for r, _ in machine_health.unhealthy_runs([old, new], since="2026-10-17T00:00:00Z")) == ["b-1", "b-2"]
