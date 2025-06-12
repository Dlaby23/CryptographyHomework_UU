"""
Kryptoanalýza substituční šifry pomocí Metropolis-Hastings algoritmu.
"""

import numpy as np
import random
from typing import Dict, Tuple, List
from substitution_cipher import SubstitutionCipher, BigramAnalysis
import pickle


class MetropolisHastingsCryptanalysis:
    """Třída pro kryptoanalýzu pomocí Metropolis-Hastings algoritmu."""
    
    def __init__(self, reference_matrix: np.ndarray, temperature: float = 1.0):
        """
        Inicializace kryptoanalýzy.
        
        Args:
            reference_matrix: Referenční bigramová matice.
            temperature: Teplota pro Metropolis-Hastings algoritmus.
        """
        self.reference_matrix = reference_matrix
        self.temperature = temperature
        self.cipher = SubstitutionCipher()
        self.analyzer = BigramAnalysis()
        
    def _swap_two_chars(self, key: Dict[str, str]) -> Dict[str, str]:
        """
        Vytvoří nový klíč prohozením dvou náhodných znaků.
        
        Args:
            key: Současný klíč.
            
        Returns:
            Dict[str, str]: Nový klíč s prohozenými znaky.
        """
        new_key = key.copy()
        chars = list(self.cipher.alphabet)
        char1, char2 = random.sample(chars, 2)
        new_key[char1], new_key[char2] = new_key[char2], new_key[char1]
        return new_key
    
    def _calculate_fitness(self, text: str) -> float:
        """
        Vypočítá fitness (vhodnost) textu podle bigramové matice.
        
        Args:
            text: Text k vyhodnocení.
            
        Returns:
            float: Fitness skóre (vyšší je lepší).
        """
        return self.analyzer.calculate_bigram_score(text, self.reference_matrix)
    
    def metropolis_hastings(self, ciphertext: str, iterations: int = 20000, 
                          print_progress: bool = True) -> Tuple[Dict[str, str], str, List[float]]:
        """
        Prolomí šifru pomocí Metropolis-Hastings algoritmu.
        
        Args:
            ciphertext: Zašifrovaný text.
            iterations: Počet iterací algoritmu.
            print_progress: Zda vypisovat průběh.
            
        Returns:
            Tuple obsahující nejlepší klíč, dešifrovaný text a historii fitness.
        """
        # Inicializace s náhodným klíčem
        current_key = self.cipher.generate_random_key()
        current_text = self.cipher.decrypt(ciphertext, current_key)
        current_fitness = self._calculate_fitness(current_text)
        
        # Sledování nejlepšího řešení
        best_key = current_key.copy()
        best_text = current_text
        best_fitness = current_fitness
        
        # Historie pro vizualizaci
        fitness_history = [current_fitness]
        
        # Adaptivní teplota
        initial_temp = self.temperature
        
        for i in range(iterations):
            # Vytvoř nového kandidáta
            candidate_key = self._swap_two_chars(current_key)
            candidate_text = self.cipher.decrypt(ciphertext, candidate_key)
            candidate_fitness = self._calculate_fitness(candidate_text)
            
            # Metropolis-Hastings krok
            delta = candidate_fitness - current_fitness
            
            # Akceptuj lepší řešení nebo horší s určitou pravděpodobností
            if delta > 0 or random.random() < np.exp(delta / self.temperature):
                current_key = candidate_key
                current_text = candidate_text
                current_fitness = candidate_fitness
                
                # Aktualizuj nejlepší řešení
                if current_fitness > best_fitness:
                    best_key = current_key.copy()
                    best_text = current_text
                    best_fitness = current_fitness
            
            fitness_history.append(current_fitness)
            
            # Postupné snižování teploty (simulated annealing)
            if i % 1000 == 0:
                self.temperature = initial_temp * (1 - i / iterations)
            
            # Výpis průběhu
            if print_progress and (i + 1) % 1000 == 0:
                print(f"Iterace {i+1}/{iterations}, nejlepší fitness: {best_fitness:.4f}")
                print(f"Ukázka textu: {best_text[:100]}")
                print()
        
        # Obnov původní teplotu
        self.temperature = initial_temp
        
        return best_key, best_text, fitness_history
    
    def break_cipher_multiple_attempts(self, ciphertext: str, attempts: int = 5, 
                                     iterations_per_attempt: int = 20000) -> Tuple[Dict[str, str], str]:
        """
        Pokusí se prolomit šifru vícekrát a vrátí nejlepší výsledek.
        
        Args:
            ciphertext: Zašifrovaný text.
            attempts: Počet pokusů.
            iterations_per_attempt: Počet iterací na pokus.
            
        Returns:
            Tuple obsahující nejlepší klíč a dešifrovaný text.
        """
        best_overall_key = None
        best_overall_text = ""
        best_overall_fitness = float('-inf')
        
        for attempt in range(attempts):
            print(f"\nPokus {attempt + 1}/{attempts}")
            key, text, _ = self.metropolis_hastings(ciphertext, iterations_per_attempt, 
                                                   print_progress=True)
            fitness = self._calculate_fitness(text)
            
            if fitness > best_overall_fitness:
                best_overall_fitness = fitness
                best_overall_key = key
                best_overall_text = text
        
        print(f"\nNejlepší celková fitness: {best_overall_fitness:.4f}")
        return best_overall_key, best_overall_text


def load_reference_matrix():
    """Načte uloženou referenční bigramovou matici."""
    try:
        with open('/Users/vaclavdlabac/Desktop/Cryptography Homework/czech_bigram_data.pkl', 'rb') as f:
            data = pickle.load(f)
            return data['matrix']
    except FileNotFoundError:
        print("Referenční matice nenalezena, vytvářím novou...")
        from create_bigram_matrix import create_and_save_bigram_matrix
        matrix, _ = create_and_save_bigram_matrix()
        return matrix


if __name__ == "__main__":
    # Test kryptoanalýzy
    cipher = SubstitutionCipher()
    
    # Vytvoř testovací text
    test_text = "TOTO_JE_TESTOVACI_TEXT_PRO_KRYPTOANALYZU_SUBSTITUCNI_SIFRY"
    
    # Zašifruj
    test_key = cipher.generate_random_key()
    encrypted = cipher.encrypt(test_text, test_key)
    
    print(f"Původní text: {test_text}")
    print(f"Zašifrovaný text: {encrypted}")
    print(f"Klíč: {cipher.key_to_string(test_key)}")
    
    # Načti referenční matici
    ref_matrix = load_reference_matrix()
    
    # Kryptoanalýza
    cryptanalysis = MetropolisHastingsCryptanalysis(ref_matrix, temperature=2.0)
    found_key, decrypted, history = cryptanalysis.metropolis_hastings(encrypted, iterations=5000)
    
    print(f"\nDešifrovaný text: {decrypted}")
    print(f"Nalezený klíč: {cipher.key_to_string(found_key)}")
    print(f"Správně dešifrováno: {decrypted == test_text}")