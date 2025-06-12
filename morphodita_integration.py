"""
Integration with MorphoDiTa for Czech language analysis.
"""

import os
import urllib.request
import zipfile

try:
    from ufal.morphodita import Tagger, Forms, TaggedLemmas, TokenRanges
    MORPHODITA_AVAILABLE = True
except ImportError:
    print("MorphoDiTa not available. Install with: pip install ufal.morphodita")
    MORPHODITA_AVAILABLE = False


class MorphoDiTaCzech:
    """Czech language analyzer using MorphoDiTa."""
    
    def __init__(self):
        self.tagger = None
        self.model_path = "czech-morfflex-pdt-161115.tagger"
        
        if MORPHODITA_AVAILABLE:
            self.setup_model()
    
    def setup_model(self):
        """Download and setup Czech model if needed."""
        if not os.path.exists(self.model_path):
            print("Downloading Czech MorphoDiTa model...")
            model_url = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11858/00-097C-0000-0023-68D8-0/czech-morfflex-pdt-161115.zip"
            
            try:
                # Download model
                urllib.request.urlretrieve(model_url, "czech_model.zip")
                
                # Extract
                with zipfile.ZipFile("czech_model.zip", 'r') as zip_ref:
                    zip_ref.extractall(".")
                
                # Clean up
                os.remove("czech_model.zip")
                
                print("Model downloaded successfully!")
            except Exception as e:
                print(f"Failed to download model: {e}")
                return
        
        # Load model
        self.tagger = Tagger.load(self.model_path)
        if not self.tagger:
            print("Failed to load MorphoDiTa model!")
        else:
            print("MorphoDiTa model loaded successfully!")
    
    def analyze_text(self, text: str) -> dict:
        """Analyze text and return linguistic features."""
        if not self.tagger or not MORPHODITA_AVAILABLE:
            return {'valid_words': 0, 'total_words': 0, 'ratio': 0.0}
        
        forms = Forms()
        lemmas = TaggedLemmas()
        tokens = TokenRanges()
        
        # Tokenize
        self.tagger.tokenizer.set_text(text)
        
        valid_words = 0
        total_words = 0
        recognized_lemmas = []
        
        while self.tagger.tokenizer.next_sentence(forms, tokens):
            self.tagger.tag(forms, lemmas)
            
            for lemma in lemmas:
                total_words += 1
                # Check if it's a valid Czech word (not unknown)
                if lemma.tag and not lemma.tag.startswith('X'):  # X = unknown
                    valid_words += 1
                    recognized_lemmas.append(lemma.lemma)
        
        ratio = valid_words / max(total_words, 1)
        
        return {
            'valid_words': valid_words,
            'total_words': total_words,
            'ratio': ratio,
            'lemmas': recognized_lemmas[:20]  # First 20 for inspection
        }
    
    def score_text(self, text: str) -> float:
        """Return a fitness score based on linguistic analysis."""
        analysis = self.analyze_text(text)
        
        # Score based on ratio of valid words
        base_score = analysis['ratio'] * 10
        
        # Bonus for longer valid words
        if analysis['valid_words'] > 10:
            base_score += 1.0
        
        return base_score


class EnhancedDictionaryScorer:
    """Enhanced dictionary scoring using both simple word list and MorphoDiTa."""
    
    def __init__(self):
        self.morpho = MorphoDiTaCzech() if MORPHODITA_AVAILABLE else None
        self.simple_words = self._load_simple_dictionary()
    
    def _load_simple_dictionary(self):
        """Load simple Czech word list."""
        words = {
            # Common Czech words
            'JE', 'JSOU', 'BYL', 'BYLA', 'BYLO', 'BUDE', 'JSEM', 'JSI', 'JSME', 'JSTE',
            'NA', 'DO', 'ZE', 'SE', 'VE', 'PO', 'PRO', 'PRI', 'OD', 'KE',
            'A', 'I', 'ANI', 'NEBO', 'ALE', 'KDYZ', 'ZE', 'ABY', 'JESTLI',
            'TEN', 'TO', 'TENTO', 'TA', 'TATO', 'TY', 'TYTO', 'ONO', 'ON', 'ONA',
            'MUJ', 'TVUJ', 'JEHO', 'JEJI', 'NAS', 'VAS', 'JEJICH', 'SVUJ',
            'KDO', 'CO', 'JAK', 'KDE', 'KDY', 'PROC', 'KTERY', 'JAKY',
            'CLOVEK', 'ROK', 'DEN', 'CAS', 'RUKA', 'OKO', 'HLAVA', 'SRDCE',
            'PRAHA', 'CESKO', 'MESTO', 'ZEME', 'VODA', 'VZDUCH', 'OHEN',
            'DOBRY', 'SPATNY', 'VELKY', 'MALY', 'NOVY', 'STARY', 'MLADY',
            'DELAT', 'MIT', 'RIKAT', 'VIDET', 'SLYSET', 'PRIJIT', 'ODEJIT',
            'JEDEN', 'DVA', 'TRI', 'CTYRI', 'PET', 'SEST', 'SEDM', 'OSM', 'DEVET', 'DESET',
            'PRVNI', 'DRUHY', 'TRETI', 'POSLEDNI', 'KAZDY', 'ZADNY', 'NEKTERY',
            'TAK', 'TADY', 'TAM', 'TED', 'PAK', 'UZ', 'JESTE', 'VZDYCKY', 'NIKDY',
            'VELMI', 'MOC', 'MALO', 'TROCHU', 'DOST', 'PRILIS', 'UPLNE'
        }
        
        # Add more words from common Czech texts
        extended_words = {
            'PRAHA', 'BRNO', 'OSTRAVA', 'PLZEN', 'CECHY', 'MORAVA', 'SLEZSKO',
            'VLTAVA', 'LABE', 'MORAVA', 'ODRA', 'DYJE', 'SAZAVA', 'BEROUNKA',
            'KAREL', 'JAN', 'PETR', 'PAVEL', 'JOSEF', 'MARIE', 'ANNA', 'EVA',
            'CAPEK', 'NEMCOVA', 'HASEK', 'NERUDA', 'MACHA', 'VRCHLICKY',
            'KRAKATIT', 'SVEJK', 'BABICKA', 'MAJ', 'KYTICE', 'POVIDKY',
            'VOJNA', 'MIR', 'LASKA', 'SMRT', 'ZIVOT', 'PRACE', 'RADOST',
            'DOM', 'STROM', 'KVET', 'LISTA', 'TRAVA', 'ZEME', 'NEBE', 'MORE'
        }
        
        words.update(extended_words)
        return words
    
    def score(self, text: str) -> float:
        """Combined scoring using both methods."""
        score = 0.0
        
        # Simple word matching
        words_in_text = text.split('_')
        matches = sum(1 for word in words_in_text if word in self.simple_words)
        simple_score = matches / max(len(words_in_text), 1) * 5
        
        # MorphoDiTa scoring if available
        if self.morpho and MORPHODITA_AVAILABLE:
            morpho_score = self.morpho.score_text(text.replace('_', ' '))
            score = simple_score * 0.4 + morpho_score * 0.6
        else:
            score = simple_score
        
        return score


if __name__ == "__main__":
    # Test the integration
    print("Testing MorphoDiTa integration...")
    
    scorer = EnhancedDictionaryScorer()
    
    # Test texts
    test_texts = [
        "PRAHA_JE_HLAVNI_MESTO_CESKE_REPUBLIKY",
        "XQZPT_QW_ERTYU_ASDFG_HJKLM_ZXCVBNM",
        "KAREL_CAPEK_NAPSAL_KNIHU_KRAKATIT",
        "DOBRY_DEN_JAK_SE_MATE_DEKUJI_DOBRE"
    ]
    
    for text in test_texts:
        score = scorer.score(text)
        print(f"\nText: {text}")
        print(f"Score: {score:.4f}")
        
        if scorer.morpho and MORPHODITA_AVAILABLE:
            analysis = scorer.morpho.analyze_text(text.replace('_', ' '))
            print(f"Valid words: {analysis['valid_words']}/{analysis['total_words']}")
            if analysis['lemmas']:
                print(f"Lemmas: {', '.join(analysis['lemmas'][:5])}")