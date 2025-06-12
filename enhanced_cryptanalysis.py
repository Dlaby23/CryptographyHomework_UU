"""
Enhanced cryptanalysis with trigrams and dictionary support.
"""

import numpy as np
import random
from typing import Dict, Tuple, List, Set
from substitution_cipher import SubstitutionCipher, BigramAnalysis
import pickle
import re


class TrigramAnalysis:
    """Trigram frequency analysis for better language modeling."""
    
    def __init__(self, alphabet: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_'):
        self.alphabet = alphabet
        self.alphabet_size = len(alphabet)
        self.char_to_index = {char: i for i, char in enumerate(alphabet)}
    
    def create_trigram_matrix(self, text: str) -> np.ndarray:
        """Create 3D trigram frequency matrix."""
        # Initialize 3D matrix with smoothing
        matrix = np.ones((self.alphabet_size, self.alphabet_size, self.alphabet_size)) * 0.1
        
        # Count trigrams
        for i in range(len(text) - 2):
            if all(c in self.char_to_index for c in text[i:i+3]):
                idx1 = self.char_to_index[text[i]]
                idx2 = self.char_to_index[text[i+1]]
                idx3 = self.char_to_index[text[i+2]]
                matrix[idx1, idx2, idx3] += 1
        
        # Normalize
        for i in range(self.alphabet_size):
            for j in range(self.alphabet_size):
                total = matrix[i, j, :].sum()
                if total > 0:
                    matrix[i, j, :] /= total
        
        return matrix
    
    def calculate_trigram_score(self, text: str, trigram_matrix: np.ndarray) -> float:
        """Calculate log probability using trigrams."""
        score = 0.0
        count = 0
        
        for i in range(len(text) - 2):
            if all(c in self.char_to_index for c in text[i:i+3]):
                idx1 = self.char_to_index[text[i]]
                idx2 = self.char_to_index[text[i+1]]
                idx3 = self.char_to_index[text[i+2]]
                prob = trigram_matrix[idx1, idx2, idx3]
                if prob > 0:
                    score += np.log(prob)
                    count += 1
        
        return score / count if count > 0 else float('-inf')


class CzechDictionary:
    """Czech dictionary for word recognition."""
    
    def __init__(self):
        self.words = set()
        self.common_words = set()
        self.load_common_words()
    
    def load_common_words(self):
        """Load most common Czech words."""
        # Common Czech words (top 100)
        self.common_words = {
            'A', 'ABY', 'AFTER', 'ALE', 'ANI', 'ANO', 'ASI', 'AZ', 'BEZ', 'BUDE', 'BUDU', 'BY', 'BYL', 'BYLA', 
            'BYLI', 'BYLO', 'BYT', 'CI', 'CLANEK', 'CLANKU', 'CO', 'COZ', 'CZ', 'DALSI', 'DO', 'DNES', 
            'DOKUD', 'DVA', 'DVE', 'HODNE', 'I', 'JA', 'JAK', 'JAKE', 'JAKO', 'JAKY', 'JE', 'JEDEN', 
            'JEDNA', 'JEDNO', 'JEHO', 'JEJI', 'JEJICH', 'JEN', 'JESTE', 'JI', 'JIZ', 'JSEM', 'JSI', 
            'JSME', 'JSOU', 'JSTE', 'K', 'KDE', 'KDO', 'KDYZ', 'KE', 'KTERA', 'KTERE', 'KTERI', 'KTERY', 
            'MA', 'MAM', 'MATE', 'ME', 'MEZI', 'MI', 'MIT', 'MNE', 'MNOU', 'MOC', 'MOCI', 'MOJ', 'MOJE', 
            'MOJI', 'MUJ', 'MUZE', 'MY', 'NA', 'NAD', 'NAM', 'NAMI', 'NAS', 'NASE', 'NASI', 'NE', 
            'NEBO', 'NECHT', 'NEJ', 'NEJSOU', 'NEZ', 'NIC', 'NICH', 'NIM', 'O', 'OD', 'ODE', 'ON', 
            'ONA', 'ONI', 'ONO', 'PAK', 'PO', 'POD', 'PODLE', 'POKUD', 'POUZE', 'PRAVE', 'PRE', 'PRED', 
            'PRES', 'PRI', 'PRO', 'PROC', 'PROTO', 'PROTOZE', 'PRVNI', 'PTA', 'RE', 'ROKU', 'S', 'SE', 
            'SI', 'SVE', 'SVUJ', 'SVYCH', 'SVYM', 'SVYMI', 'TA', 'TAK', 'TAKE', 'TAKY', 'TAM', 'TAMHLE', 
            'TATO', 'TE', 'TEBE', 'TED', 'TEDY', 'TEN', 'TENTO', 'TIPY', 'TO', 'TOBE', 'TOHLE', 'TOHO', 
            'TOHOTO', 'TOM', 'TOMTO', 'TOMU', 'TOMUTO', 'TU', 'TUTO', 'TVA', 'TVE', 'TVJ', 'TVOJE', 
            'TVOJI', 'TY', 'TYTO', 'U', 'UZ', 'V', 'VAM', 'VAMI', 'VAS', 'VASE', 'VASI', 'VE', 'VEDLE', 
            'VIC', 'VICE', 'VSAK', 'VSECHNO', 'VY', 'Z', 'ZA', 'ZDE', 'ZE', 'ZE'
        }
        
        # Add with underscores for our format
        words_with_underscores = set()
        for word in self.common_words:
            words_with_underscores.add(word)
            if len(word) > 1:
                words_with_underscores.add('_' + word)
                words_with_underscores.add(word + '_')
                words_with_underscores.add('_' + word + '_')
        
        self.words = words_with_underscores
    
    def count_words(self, text: str) -> Tuple[int, float]:
        """Count recognized words in text."""
        words_found = 0
        total_length = 0
        
        # Split by underscores
        potential_words = text.split('_')
        
        for word in potential_words:
            if len(word) > 0:
                total_length += len(word)
                if word in self.common_words:
                    words_found += 1
        
        # Also check with underscores
        for word in self.words:
            if word in text:
                words_found += 0.5  # Partial credit
        
        return words_found, words_found / max(len(potential_words), 1)


class EnhancedMetropolisHastings:
    """Enhanced cryptanalysis with trigrams and dictionary."""
    
    def __init__(self, bigram_matrix: np.ndarray, trigram_matrix: np.ndarray = None, 
                 use_dictionary: bool = True, temperature: float = 2.0):
        self.bigram_matrix = bigram_matrix
        self.trigram_matrix = trigram_matrix
        self.use_dictionary = use_dictionary
        self.temperature = temperature
        self.initial_temperature = temperature
        
        self.cipher = SubstitutionCipher()
        self.bigram_analyzer = BigramAnalysis()
        self.trigram_analyzer = TrigramAnalysis() if trigram_matrix is not None else None
        self.dictionary = CzechDictionary() if use_dictionary else None
        
        # Weights for different scoring components
        self.bigram_weight = 0.4
        self.trigram_weight = 0.4
        self.dictionary_weight = 0.2
    
    def _calculate_comprehensive_fitness(self, text: str) -> float:
        """Calculate fitness using multiple metrics."""
        score = 0.0
        
        # Bigram score
        bigram_score = self.bigram_analyzer.calculate_bigram_score(text, self.bigram_matrix)
        score += self.bigram_weight * bigram_score
        
        # Trigram score
        if self.trigram_matrix is not None:
            trigram_score = self.trigram_analyzer.calculate_trigram_score(text, self.trigram_matrix)
            score += self.trigram_weight * trigram_score
        else:
            score += self.trigram_weight * bigram_score  # Fallback to bigram
        
        # Dictionary score
        if self.dictionary:
            word_count, word_ratio = self.dictionary.count_words(text)
            dict_score = word_ratio * 10  # Scale to similar range
            score += self.dictionary_weight * dict_score
        
        return score
    
    def _smart_key_modification(self, key: Dict[str, str], text: str) -> Dict[str, str]:
        """Smart key modification based on analysis."""
        new_key = key.copy()
        
        # 80% chance of simple swap
        if random.random() < 0.8:
            chars = list(self.cipher.alphabet)
            char1, char2 = random.sample(chars, 2)
            new_key[char1], new_key[char2] = new_key[char2], new_key[char1]
        else:
            # 20% chance of targeted swap based on frequency
            # Find characters that might be misplaced
            decrypted = self.cipher.decrypt(text, key)
            
            # Look for unlikely patterns
            unlikely_bigrams = []
            for i in range(len(decrypted) - 1):
                if decrypted[i:i+2] in ['QX', 'XQ', 'QZ', 'ZQ', 'QW', 'WQ']:
                    unlikely_bigrams.append((decrypted[i], decrypted[i+1]))
            
            if unlikely_bigrams:
                # Try to fix unlikely bigram
                char_to_swap = random.choice([c for bigram in unlikely_bigrams for c in bigram])
                other_char = random.choice([c for c in self.cipher.alphabet if c != char_to_swap])
                
                # Find which original chars map to these
                for k, v in key.items():
                    if v == char_to_swap:
                        char1 = k
                    if v == other_char:
                        char2 = k
                
                new_key[char1], new_key[char2] = new_key[char2], new_key[char1]
        
        return new_key
    
    def _generate_initial_key_by_frequency(self, ciphertext: str) -> Dict[str, str]:
        """Generate initial key based on frequency analysis."""
        # Czech letter frequencies (approximate)
        czech_freq_order = 'EANTOIVLSRKUDMHPCZBJGFYW_QX'
        
        # Count cipher frequencies
        cipher_freq = {}
        for char in self.cipher.alphabet:
            cipher_freq[char] = ciphertext.count(char)
        
        # Sort by frequency
        sorted_cipher = sorted(cipher_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Map most frequent cipher chars to most frequent Czech chars
        key = {}
        for i, (cipher_char, _) in enumerate(sorted_cipher):
            if i < len(czech_freq_order):
                key[cipher_char] = czech_freq_order[i]
            else:
                key[cipher_char] = cipher_char
        
        return key
    
    def enhanced_metropolis_hastings(self, ciphertext: str, iterations: int = 30000,
                                   print_progress: bool = True) -> Tuple[Dict[str, str], str, List[float]]:
        """Enhanced M-H with all improvements."""
        
        # Try both random and frequency-based initial keys
        initial_keys = [
            self.cipher.generate_random_key(),
            self._generate_initial_key_by_frequency(ciphertext)
        ]
        
        best_overall_key = None
        best_overall_text = ""
        best_overall_fitness = float('-inf')
        best_overall_history = []
        
        for init_key in initial_keys:
            # Reset temperature
            self.temperature = self.initial_temperature
            
            current_key = init_key
            current_text = self.cipher.decrypt(ciphertext, current_key)
            current_fitness = self._calculate_comprehensive_fitness(current_text)
            
            best_key = current_key.copy()
            best_text = current_text
            best_fitness = current_fitness
            
            fitness_history = [current_fitness]
            
            # Adaptive cooling schedule
            no_improvement_count = 0
            
            for i in range(iterations):
                # Smart key modification
                candidate_key = self._smart_key_modification(current_key, ciphertext)
                candidate_text = self.cipher.decrypt(ciphertext, candidate_key)
                candidate_fitness = self._calculate_comprehensive_fitness(candidate_text)
                
                # Metropolis-Hastings acceptance
                delta = candidate_fitness - current_fitness
                
                if delta > 0 or random.random() < np.exp(delta / self.temperature):
                    current_key = candidate_key
                    current_text = candidate_text
                    current_fitness = candidate_fitness
                    
                    if current_fitness > best_fitness:
                        best_key = current_key.copy()
                        best_text = current_text
                        best_fitness = current_fitness
                        no_improvement_count = 0
                    else:
                        no_improvement_count += 1
                else:
                    no_improvement_count += 1
                
                fitness_history.append(best_fitness)
                
                # Adaptive temperature
                if i % 1000 == 0:
                    if no_improvement_count > 500:
                        # Reheat if stuck
                        self.temperature = self.initial_temperature * 0.5
                        no_improvement_count = 0
                    else:
                        # Cool down
                        self.temperature = self.initial_temperature * (1 - i / iterations)
                
                if print_progress and (i + 1) % 2000 == 0:
                    if self.dictionary:
                        word_count, word_ratio = self.dictionary.count_words(best_text)
                        print(f"Iteration {i+1}/{iterations}, fitness: {best_fitness:.4f}, words: {word_count}")
                    else:
                        print(f"Iteration {i+1}/{iterations}, fitness: {best_fitness:.4f}")
                    print(f"Sample: {best_text[:100]}")
            
            if best_fitness > best_overall_fitness:
                best_overall_fitness = best_fitness
                best_overall_key = best_key
                best_overall_text = best_text
                best_overall_history = fitness_history
        
        return best_overall_key, best_overall_text, best_overall_history


def create_enhanced_bigram_trigram_matrices(corpus_file: str = 'czech_corpus_enhanced.txt'):
    """Create both bigram and trigram matrices from corpus."""
    
    print("Loading corpus...")
    try:
        with open(corpus_file, 'r', encoding='utf-8') as f:
            corpus = f.read()
    except FileNotFoundError:
        print(f"Corpus file {corpus_file} not found. Using original Krakatit.")
        with open('krakatit_processed.txt', 'r', encoding='utf-8') as f:
            corpus = f.read()
    
    print(f"Corpus size: {len(corpus):,} characters")
    
    # Create bigram matrix
    print("Creating bigram matrix...")
    bigram_analyzer = BigramAnalysis()
    bigram_matrix = bigram_analyzer.create_bigram_matrix(corpus)
    
    # Create trigram matrix
    print("Creating trigram matrix...")
    trigram_analyzer = TrigramAnalysis()
    trigram_matrix = trigram_analyzer.create_trigram_matrix(corpus)
    
    # Save matrices
    print("Saving matrices...")
    np.save('czech_bigram_enhanced.npy', bigram_matrix)
    np.save('czech_trigram.npy', trigram_matrix)
    
    with open('czech_enhanced_data.pkl', 'wb') as f:
        pickle.dump({
            'bigram_matrix': bigram_matrix,
            'trigram_matrix': trigram_matrix,
            'alphabet': bigram_analyzer.alphabet,
            'corpus_size': len(corpus)
        }, f)
    
    print("Enhanced matrices created!")
    return bigram_matrix, trigram_matrix


if __name__ == "__main__":
    # Test enhanced cryptanalysis
    cipher = SubstitutionCipher()
    
    test_text = "TENTO_TEXT_OBSAHUJE_CESKE_SLOVA_JAKO_JE_PRAHA_NEBO_VODA_A_TAKE_DELSI_VETY"
    test_key = cipher.generate_random_key()
    encrypted = cipher.encrypt(test_text, test_key)
    
    print(f"Original: {test_text}")
    print(f"Encrypted: {encrypted}")
    
    # Load or create matrices
    try:
        with open('czech_enhanced_data.pkl', 'rb') as f:
            data = pickle.load(f)
            bigram_matrix = data['bigram_matrix']
            trigram_matrix = data['trigram_matrix']
    except FileNotFoundError:
        print("Creating enhanced matrices...")
        bigram_matrix, trigram_matrix = create_enhanced_bigram_trigram_matrices()
    
    # Run enhanced cryptanalysis
    print("\nRunning enhanced cryptanalysis...")
    analyzer = EnhancedMetropolisHastings(bigram_matrix, trigram_matrix, use_dictionary=True)
    found_key, decrypted, history = analyzer.enhanced_metropolis_hastings(encrypted, iterations=10000)
    
    print(f"\nDecrypted: {decrypted}")
    print(f"Success: {decrypted == test_text}")