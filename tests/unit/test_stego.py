from app.stego.analyzers.bitplane import BitplaneAnalyzer
from app.stego.analyzers.lsb import LSBAnalyzer


def test_stego_instantiation() -> None:
    # Mostly checking that instantiation works without error
    # since PIL might not be present or we need complex fixtures for full LSB test
    analyzer = LSBAnalyzer()
    bitplane = BitplaneAnalyzer()
    
    assert analyzer is not None
    assert bitplane is not None
