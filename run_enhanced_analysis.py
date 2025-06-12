"""
Run enhanced cryptanalysis on test files.
"""

import os
import time
from enhanced_cryptanalysis import EnhancedMetropolisHastings, create_enhanced_bigram_trigram_matrices
from cryptanalysis import load_reference_matrix
from substitution_cipher import SubstitutionCipher
import pickle
import numpy as np


def run_comparison():
    """Compare original vs enhanced cryptanalysis."""
    
    # Test on a sample file
    test_file = "/Users/vaclavdlabac/Desktop/Cryptography Homework/Testovaci_soubory/text_500_sample_1_ciphertext.txt"
    
    if not os.path.exists(test_file):
        print("Test file not found!")
        return
    
    # Load ciphertext
    with open(test_file, 'r', encoding='utf-8') as f:
        ciphertext = f.read().strip()
    
    print(f"Testing on: {os.path.basename(test_file)}")
    print(f"Ciphertext length: {len(ciphertext)}")
    print(f"First 100 chars: {ciphertext[:100]}")
    print("\n" + "="*60 + "\n")
    
    cipher = SubstitutionCipher()
    
    # 1. Original method
    print("1. ORIGINAL METHOD (bigrams only)")
    print("-" * 30)
    
    from cryptanalysis import MetropolisHastingsCryptanalysis
    
    ref_matrix = load_reference_matrix()
    original_analyzer = MetropolisHastingsCryptanalysis(ref_matrix, temperature=2.0)
    
    start_time = time.time()
    orig_key, orig_text, orig_history = original_analyzer.metropolis_hastings(
        ciphertext, iterations=10000, print_progress=False
    )
    orig_time = time.time() - start_time
    
    print(f"Time: {orig_time:.2f}s")
    print(f"Final fitness: {orig_history[-1]:.4f}")
    print(f"Result: {orig_text[:100]}...")
    
    # 2. Enhanced method
    print("\n2. ENHANCED METHOD (bigrams + trigrams + dictionary)")
    print("-" * 30)
    
    # Load or create enhanced matrices
    try:
        with open('czech_enhanced_data.pkl', 'rb') as f:
            data = pickle.load(f)
            bigram_matrix = data['bigram_matrix']
            trigram_matrix = data['trigram_matrix']
    except FileNotFoundError:
        print("Creating enhanced matrices... (this may take a few minutes)")
        # First fetch the corpus
        print("Fetching enhanced corpus...")
        from fetch_enhanced_corpus import fetch_all_czech_texts
        corpus, _ = fetch_all_czech_texts()
        
        # Then create matrices
        bigram_matrix, trigram_matrix = create_enhanced_bigram_trigram_matrices()
    
    enhanced_analyzer = EnhancedMetropolisHastings(
        bigram_matrix, trigram_matrix, use_dictionary=True, temperature=2.0
    )
    
    start_time = time.time()
    enh_key, enh_text, enh_history = enhanced_analyzer.enhanced_metropolis_hastings(
        ciphertext, iterations=10000, print_progress=True
    )
    enh_time = time.time() - start_time
    
    print(f"\nTime: {enh_time:.2f}s")
    print(f"Final fitness: {enh_history[-1]:.4f}")
    print(f"Result: {enh_text[:100]}...")
    
    # Compare results
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    print(f"Original fitness: {orig_history[-1]:.4f}")
    print(f"Enhanced fitness: {enh_history[-1]:.4f}")
    print(f"Improvement: {((enh_history[-1] - orig_history[-1]) / abs(orig_history[-1]) * 100):.1f}%")
    print(f"Speed difference: {enh_time - orig_time:.2f}s")
    
    # Check if results are similar
    matching_chars = sum(1 for o, e in zip(orig_text, enh_text) if o == e)
    similarity = matching_chars / len(orig_text) * 100
    print(f"Result similarity: {similarity:.1f}%")
    
    # Save comparison plot
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(orig_history[:5000], label='Original', alpha=0.7)
    plt.plot(enh_history[:5000], label='Enhanced', alpha=0.7)
    plt.xlabel('Iteration')
    plt.ylabel('Fitness')
    plt.title('Fitness Evolution Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    final_iterations = min(1000, len(orig_history), len(enh_history))
    plt.plot(orig_history[-final_iterations:], label='Original', alpha=0.7)
    plt.plot(enh_history[-final_iterations:], label='Enhanced', alpha=0.7)
    plt.xlabel('Iteration')
    plt.ylabel('Fitness')
    plt.title('Final 1000 Iterations')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('enhanced_comparison.png', dpi=150)
    print("\nComparison plot saved as 'enhanced_comparison.png'")


if __name__ == "__main__":
    run_comparison()