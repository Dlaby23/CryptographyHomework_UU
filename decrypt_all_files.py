"""
Skript pro dešifrování všech testovacích souborů.
"""

import os
import glob
from cryptanalysis import MetropolisHastingsCryptanalysis, load_reference_matrix
from substitution_cipher import SubstitutionCipher
import time


def decrypt_file(filepath: str, cryptanalysis: MetropolisHastingsCryptanalysis, 
                 cipher: SubstitutionCipher, iterations: int = 20000):
    """
    Dešifruje jeden soubor.
    
    Args:
        filepath: Cesta k zašifrovanému souboru.
        cryptanalysis: Instance kryptoanalýzy.
        cipher: Instance šifry.
        iterations: Počet iterací algoritmu.
    """
    # Načti zašifrovaný text
    with open(filepath, 'r', encoding='utf-8') as f:
        ciphertext = f.read().strip()
    
    print(f"\nDešifruji soubor: {os.path.basename(filepath)}")
    print(f"Délka textu: {len(ciphertext)} znaků")
    
    # Extrakce informací z názvu souboru
    filename = os.path.basename(filepath)
    parts = filename.replace('_ciphertext.txt', '').split('_')
    text_length = parts[1]  # např. "1000"
    sample_id = parts[3]    # např. "1"
    
    # Dešifrování
    start_time = time.time()
    best_key, best_text, fitness_history = cryptanalysis.metropolis_hastings(
        ciphertext, iterations=iterations, print_progress=False
    )
    end_time = time.time()
    
    print(f"Dešifrování dokončeno za {end_time - start_time:.2f} sekund")
    print(f"Konečná shoda: {fitness_history[-1]:.4f}") # Větší číslo je lepší (je to log takže to ukazuje zaporne hodnoty)
    
    # Uložení výsledků
    output_dir = "decrypted_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Uložení dešifrovaného textu
    plaintext_filename = f"text_{text_length}_sample_{sample_id}_plaintext.txt"
    plaintext_path = os.path.join(output_dir, plaintext_filename)
    with open(plaintext_path, 'w', encoding='utf-8') as f:
        f.write(best_text)
    
    # Uložení klíče
    key_filename = f"text_{text_length}_sample_{sample_id}_key.txt"
    key_path = os.path.join(output_dir, key_filename)
    with open(key_path, 'w', encoding='utf-8') as f:
        f.write(cipher.key_to_string(best_key))
    
    print(f"Výsledky uloženy: {plaintext_filename}, {key_filename}")
    
    return best_text, best_key, fitness_history[-1]


def decrypt_all_test_files():
    """Dešifruje všechny testovací soubory."""
    
    # Najdi testovací soubory
    test_files_pattern = "test_files/*_ciphertext.txt"
    test_files = glob.glob(test_files_pattern)
    
    if not test_files:
        print("Žádné testovací soubory nenalezeny!")
        return
    
    print(f"Nalezeno {len(test_files)} testovacích souborů")
    
    # Načti referenční matici
    ref_matrix = load_reference_matrix()
    
    # Inicializace
    cipher = SubstitutionCipher()
    cryptanalysis = MetropolisHastingsCryptanalysis(ref_matrix, temperature=2.0)
    
    # Statistiky
    results = []
    
    # Zpracuj každý soubor
    for i, filepath in enumerate(sorted(test_files), 1):
        print(f"\n{'='*60}")
        print(f"Zpracovávám soubor {i}/{len(test_files)}")
        
        try:
            plaintext, key, fitness = decrypt_file(filepath, cryptanalysis, cipher, iterations=20000)
            results.append({
                'file': os.path.basename(filepath),
                'fitness': fitness,
                'success': True
            })
        except Exception as e:
            print(f"Chyba při zpracování souboru {filepath}: {e}")
            results.append({
                'file': os.path.basename(filepath),
                'fitness': 0,
                'success': False
            })
    
    # Souhrn výsledků
    print(f"\n{'='*60}")
    print("SOUHRN VÝSLEDKŮ")
    print(f"{'='*60}")
    
    successful = sum(1 for r in results if r['success'])
    print(f"Úspěšně dešifrováno: {successful}/{len(results)}")
    
    if successful > 0:
        avg_fitness = sum(r['fitness'] for r in results if r['success']) / successful
        print(f"Průměrná shoda: {avg_fitness:.4f}")
    
    # Uložení souhrnu
    summary_path = "decrypted_results/summary.txt"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("SOUHRN DEŠIFROVÁNÍ\n")
        f.write("==================\n\n")
        for result in results:
            status = "ÚSPĚCH" if result['success'] else "CHYBA"
            f.write(f"{result['file']}: {status} (fitness: {result['fitness']:.4f})\n")
        f.write(f"\nCelkem úspěšně: {successful}/{len(results)}\n")


if __name__ == "__main__":
    decrypt_all_test_files()