from src.processing import validar_peso_carga


def test_validar_peso_carga_limite():
    assert validar_peso_carga(5000) is True
    assert validar_peso_carga(15000) is False
    assert validar_peso_carga(-10) is True
