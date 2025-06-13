"""
Vytvoření bigramové matice z českého textu.
"""

import numpy as np
from substitution_cipher import BigramAnalysis
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import os


def create_and_save_bigram_matrix():
    """Vytvoří a uloží bigramovou matici z textu Krakatit."""
    
    # Načtení textu
    print("Načítám zpracovaný text...")
    with open('data/krakatit_processed.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"Délka textu: {len(text)} znaků")
    
    # Vytvoření bigramové analýzy
    analyzer = BigramAnalysis()
    
    print("Vytvářím bigramovou matici...")
    bigram_matrix = analyzer.create_bigram_matrix(text)
    
    # Uložení matice
    os.makedirs('data', exist_ok=True)
    np.save('data/czech_bigram_matrix.npy', bigram_matrix)
    
    # Uložení také jako pickle pro snadnější načítání s metadaty
    with open('data/czech_bigram_data.pkl', 'wb') as f:
        pickle.dump({
            'matrix': bigram_matrix,
            'alphabet': analyzer.alphabet,
            'source_text_length': len(text)
        }, f)
    
    print("Bigramová matice uložena!")
    
    # Statistiky
    print("\nStatistiky bigramové matice:")
    print(f"Rozměry: {bigram_matrix.shape}")
    print(f"Min pravděpodobnost: {bigram_matrix.min():.6f}")
    print(f"Max pravděpodobnost: {bigram_matrix.max():.6f}")
    print(f"Průměrná pravděpodobnost: {bigram_matrix.mean():.6f}")
    
    # Nejčastější bigramy
    print("\nNejčastější bigramy:")
    indices = np.unravel_index(np.argsort(bigram_matrix, axis=None)[-10:], bigram_matrix.shape)
    for i in range(9, -1, -1):
        row, col = indices[0][i], indices[1][i]
        bigram = analyzer.alphabet[row] + analyzer.alphabet[col]
        prob = bigram_matrix[row, col]
        print(f"  {bigram}: {prob:.4f}")
    
    return bigram_matrix, analyzer


def visualize_bigram_matrix(matrix, analyzer):
    """Vizualizuje bigramovou matici."""
    
    plt.figure(figsize=(12, 10))
    
    # Použij logaritmické měřítko pro lepší vizualizaci
    log_matrix = np.log10(matrix + 1e-10)
    
    sns.heatmap(log_matrix, 
                xticklabels=list(analyzer.alphabet),
                yticklabels=list(analyzer.alphabet),
                cmap='viridis',
                cbar_kws={'label': 'log10(pravděpodobnost)'})
    
    plt.title('Bigramová matice českého textu (log měřítko)')
    plt.xlabel('Druhý znak')
    plt.ylabel('První znak')
    plt.tight_layout()
    plt.savefig('data/bigram_matrix_visualization.png', dpi=150)
    plt.close()
    
    print("Vizualizace uložena jako 'bigram_matrix_visualization.png'")


if __name__ == "__main__":
    matrix, analyzer = create_and_save_bigram_matrix()
    visualize_bigram_matrix(matrix, analyzer)