import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import p1_finetune


class FakeTok:
    """Jetons : un caractère = un identifiant ; [CLS]=1 au début et [SEP]=2 à la fin quand les jetons spéciaux sont demandés."""

    def encode(self, text, add_special_tokens=True):
        body = [ord(c) for c in text] if text != "[...]" else [900]
        return [1, *body, 2] if add_special_tokens else body


def test_texte_court_garde_les_jetons_speciaux_sans_marqueur():
    assert p1_finetune.build_inputs(FakeTok(), ["abc"], max_len=10) == [[1, 97, 98, 99, 2]]


def test_texte_long_garde_max_len_sur_deux_tetes_plus_marqueur_et_jetons_speciaux():
    out = p1_finetune.build_inputs(FakeTok(), ["a" * 50 + "b" * 50], max_len=12)[0]
    assert len(out) == 12 + 1 + 2 and out[0] == 1 and out[-1] == 2 and 900 in out
    assert out[1] == ord("a") and out[-2] == ord("b")
