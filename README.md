# CryptographyHomework_UU
**SimpleSubCipher** – Python library for monoalphabetic substitution cipher cryptanalysis. Features: encrypt/decrypt (A-Z + "_"), Czech bigram frequency analysis from Krakatit corpus (450k+ chars), automated breaking via Metropolis-Hastings (20k iterations). Includes clean API, CLI tools, Jupyter demo, and bulk decryption with formatted export.

## Instalace
```bash
# 1. Klonování repozitáře
git clone <repository-url>
cd CryptographyHomework_UU

# 2. Instalace závislostí
pip install -r requirements.txt
```

## Struktura projektu
- `substitution_cipher.py` - Základní knihovna pro práci se substituční šifrou
- `cryptanalysis.py` - Implementace Metropolis-Hastings algoritmu pro kryptoanalýzu
- `fetch_krakatit_improved.py` - Vytvoření českého referenčního textu (funguje offline)
- `create_bigram_matrix.py` - Vytvoření bigramové matice
- `decrypt_all_files.py` - Dešifrování testovacích souborů
- `demonstration.ipynb` - Jupyter notebook s demonstrací
- `data/` - Adresář pro uložení dat (vytvoří se automaticky)
- `test_files/` - Adresář pro testovací soubory k dešifrování
- `decrypted_results/` - Adresář pro výsledky dešifrování

## Rychlý start
1. Stažení referenčního textu a vytvoření bigramové matice:
```bash
python3 fetch_krakatit.py
python3 create_bigram_matrix.py
```

2. Dešifrování testovacích souborů:
```bash
# Umísti soubory *_ciphertext.txt do složky test_files/
python3 decrypt_all_files.py
```

3. Spuštění demonstrace:
```bash
jupyter notebook demonstration.ipynb
```

## Použití knihovny
### Šifrování a dešifrování
```python
from substitution_cipher import SubstitutionCipher

cipher = SubstitutionCipher()

# Vygenerování klíče
key = cipher.generate_random_key()

# Šifrování
plaintext = "AHOJ_SVETE"
ciphertext = cipher.encrypt(plaintext, key)

# Dešifrování
decrypted = cipher.decrypt(ciphertext, key)
```

### Kryptoanalýza
```python
from cryptanalysis import MetropolisHastingsCryptanalysis, load_reference_matrix

# Načtení referenční matice
ref_matrix = load_reference_matrix()

# Kryptoanalýza
cryptanalysis = MetropolisHastingsCryptanalysis(ref_matrix)
found_key, plaintext, history = cryptanalysis.metropolis_hastings(ciphertext, iterations=20000)
```

## Poznámky
### Jupyter notebook
Notebook musí být spuštěn postupně od začátku. Použijte:
- "Cell" → "Run All" pro spuštění všech buněk
- Nebo Shift+Enter pro postupné spouštění jednotlivých buněk

### Struktura souborů
Testovací soubory k dešifrování jsou již připraveny ve složce `test_files/`

## Autor
Václav Dlabač alias Dlaby

"""Tento projekt byl vytvořen pro vzdělávací účely na žádost Unicorn University."""