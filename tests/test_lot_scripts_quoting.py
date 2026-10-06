"""Le chemin du dépôt contient des espaces : une redirection `> $LOGDIR/x` non guillemetée dans un script de lot écrit dans un fichier parasite
(`/mnt/d/Projets`) et donne des arguments parasites au programme (incident du 06/10/2026, RM-45 sorti en code 2)."""
import re
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
UNQUOTED_REDIRECT = re.compile(r"\d*>>?\s*\$\{?LOGDIR")


def test_aucune_redirection_vers_logdir_sans_guillemets():
    offenders = []
    for path in sorted(SCRIPTS.glob("run_*.sh")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.lstrip().startswith("#") and UNQUOTED_REDIRECT.search(line):
                offenders.append(f"{path.name}:{number}")
    assert not offenders, "redirection vers $LOGDIR sans guillemets : " + ", ".join(offenders)


def test_le_detecteur_distingue_guillemets_et_absence_de_guillemets():
    assert UNQUOTED_REDIRECT.search('run_lot "$LOG" x 3 bash -c "py > $LOGDIR/x.out 2>&1"')
    assert not UNQUOTED_REDIRECT.search('run_lot "$LOG" x 3 bash -c "py > \\"$LOGDIR/x.out\\" 2>&1"')
    assert not UNQUOTED_REDIRECT.search('echo ok >> "$LOGDIR/x.log"')
