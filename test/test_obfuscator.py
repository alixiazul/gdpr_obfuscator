from src.obfuscator import obfuscate

def test_obfuscator():
    obj = obfuscate()

    assert obj == None