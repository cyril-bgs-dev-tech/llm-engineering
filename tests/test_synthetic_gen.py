from llmft import synthetic_gen


def test_prompt_contains_source_text_and_forbids_copying_names() -> None:
    p = synthetic_gen.build_prompt("Compte rendu : patient de 60 ans admis pour pneumonie.", style_hint="court")
    assert "pneumonie" in p and "court" in p
    assert "ne recopie" in p.lower() and "fictif" in p.lower()


def test_record_ids_are_stable_and_carry_the_source() -> None:
    r = synthetic_gen.make_record(source_id="P12", label="XXII", text="texte", index=1)
    assert r == {"id": "synth-P12-1", "source_id": "P12", "label": "XXII", "text": "texte"}


def test_too_short_or_too_similar_outputs_are_rejected() -> None:
    src = "le patient est hospitalisé pour une douleur thoracique avec dyspnée et fièvre depuis trois jours " * 3
    assert not synthetic_gen.acceptable("trop court", src)
    assert not synthetic_gen.acceptable(src, src)
    assert synthetic_gen.acceptable("Une femme de quarante ans consulte pour une toux persistante et une asthénie, sans fièvre. " * 6, src)
