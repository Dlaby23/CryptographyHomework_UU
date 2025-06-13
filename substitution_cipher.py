"""
Knihovna pro šifrování, dešifrování a kryptoanalýzu substituční šifry.
"""

import random
import string
from typing import Dict, List, Tuple
import numpy as np


class SubstitutionCipher:
    """Třída pro práci se substituční šifrou."""
    
    def __init__(self):
        """Inicializace s výchozí abecedou."""
        self.alphabet = string.ascii_uppercase + '_'
        self.alphabet_size = len(self.alphabet)
        
    def generate_random_key(self) -> Dict[str, str]:
        """
        Vygeneruje náhodný klíč (permutaci abecedy).
        
        Returns:
            Dict[str, str]: Slovník mapující původní znaky na šifrované.
        """
        shuffled = list(self.alphabet)
        random.shuffle(shuffled)
        return dict(zip(self.alphabet, shuffled))
    
    def key_to_string(self, key: Dict[str, str]) -> str:
        """
        Převede klíč na řetězec pro snadné uložení.
        
        Args:
            key: Slovník reprezentující klíč.
            
        Returns:
            str: Řetězec reprezentující permutaci.
        """
        return ''.join(key[char] for char in self.alphabet)
    
    def string_to_key(self, key_string: str) -> Dict[str, str]:
        """
        Převede řetězec zpět na klíč.
        
        Args:
            key_string: Řetězec reprezentující permutaci.
            
        Returns:
            Dict[str, str]: Slovník mapující původní znaky na šifrované.
        """
        if len(key_string) != self.alphabet_size:
            raise ValueError(f"Klíč musí mít délku {self.alphabet_size}")
        return dict(zip(self.alphabet, key_string))
    
    def encrypt(self, plaintext: str, key: Dict[str, str]) -> str:
        """
        Zašifruje text pomocí daného klíče.
        
        Args:
            plaintext: Text k zašifrování (velká písmena a podtržítka).
            key: Klíč pro šifrování.
            
        Returns:
            str: Zašifrovaný text.
        """
        return ''.join(key.get(char, char) for char in plaintext)
    
    def decrypt(self, ciphertext: str, key: Dict[str, str]) -> str:
        """
        Dešifruje text pomocí daného klíče.
        
        Args:
            ciphertext: Zašifrovaný text.
            key: Klíč pro šifrování.
            
        Returns:
            str: Dešifrovaný text.
        """
        # Vytvoříme inverzní klíč
        inverse_key = {v: k for k, v in key.items()}
        return ''.join(inverse_key.get(char, char) for char in ciphertext)
    
    def preprocess_text(self, text: str) -> str:
        """
        Předpřipraví text pro šifrování.
        
        Args:
            text: Vstupní text.
            
        Returns:
            str: Text obsahující pouze velká písmena A-Z a podtržítka.
        """
        # Převod na velká písmena
        text = text.upper()
        
        # Náhrada diakritiky
        replacements = {
            'Á': 'A', 'Č': 'C', 'Ď': 'D', 'É': 'E', 'Ě': 'E',
            'Í': 'I', 'Ň': 'N', 'Ó': 'O', 'Ř': 'R', 'Š': 'S',
            'Ť': 'T', 'Ú': 'U', 'Ů': 'U', 'Ý': 'Y', 'Ž': 'Z'
        }
        
        for czech_char, latin_char in replacements.items():
            text = text.replace(czech_char, latin_char)
        
        # Náhrada mezer podtržítky a odstranění ostatních znaků
        result = []
        for char in text:
            if char in string.ascii_uppercase:
                result.append(char)
            elif char == ' ':
                result.append('_')
        
        # Odstranění vícenásobných podtržítek
        processed = ''.join(result)
        while '__' in processed:
            processed = processed.replace('__', '_')
        
        return processed


class BigramAnalysis:
    """Třída pro analýzu bigramů v textu."""
    
    def __init__(self, alphabet: str = string.ascii_uppercase + '_'):
        """
        Inicializace s danou abecedou.
        
        Args:
            alphabet: Použitá abeceda.
        """
        self.alphabet = alphabet
        self.alphabet_size = len(alphabet)
        self.char_to_index = {char: i for i, char in enumerate(alphabet)}
    
    def create_bigram_matrix(self, text: str) -> np.ndarray:
        """
        Vytvoří bigramovou matici z textu.
        
        Args:
            text: Text pro analýzu.
            
        Returns:
            np.ndarray: Matice pravděpodobností bigramů.
        """
        # Inicializace matice s pseudocounty pro vyhlazení
        matrix = np.ones((self.alphabet_size, self.alphabet_size)) * 0.5
        
        # Počítání bigramů
        for i in range(len(text) - 1):
            if text[i] in self.char_to_index and text[i + 1] in self.char_to_index:
                row = self.char_to_index[text[i]]
                col = self.char_to_index[text[i + 1]]
                matrix[row, col] += 1
        
        # Normalizace na pravděpodobnosti
        row_sums = matrix.sum(axis=1)
        matrix = matrix / row_sums[:, np.newaxis]
        
        return matrix
    
    def calculate_bigram_score(self, text: str, reference_matrix: np.ndarray) -> float:
        """
        Vypočítá skóre textu podle reference bigramové matice.
        
        Args:
            text: Text k vyhodnocení.
            reference_matrix: Referenční bigramová matice.
            
        Returns:
            float: Log-pravděpodobnost textu.
        """
        score = 0.0
        count = 0
        
        for i in range(len(text) - 1):
            if text[i] in self.char_to_index and text[i + 1] in self.char_to_index:
                row = self.char_to_index[text[i]]
                col = self.char_to_index[text[i + 1]]
                prob = reference_matrix[row, col]
                if prob > 0:
                    score += np.log(prob)
                    count += 1
        
        return score / count if count > 0 else float('-inf')