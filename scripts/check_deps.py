import importlib
mods = ['numpy','pandas','matplotlib','scipy','pymedphys']
for m in mods:
    try:
        importlib.import_module(m)
        print(f"{m}: OK")
    except Exception as e:
        print(f"{m}: MISSING - {e}")
