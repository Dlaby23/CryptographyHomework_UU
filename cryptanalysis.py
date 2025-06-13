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
    
    def break_cipher_multiple_attempts(self, ciphertext: str, attempts: int = 5, iterations_per_attempt: int = 20000) -> Tuple[Dict[str, str], str]:
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
        with open('data/czech_bigram_data.pkl', 'rb') as f:
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
    test_text = "NEBYLA_A_JA_V_LENOSCE_JAKO_KUS_DREVA_VIS_UNAVEN_PRILIS_PRACE_A_NAJEDNOU_PRASK_JA_LETEL_NA_ZEM_OKNA_TO_VYRAZILO_A_ZAROVKA_PRYC_DETONACE_JAKO_JAKO_KDYZ_BOUCHNE_LYDITOVA_PATRONA_STRASTRASNA_BRIZANCE_JA_JA_NEJDRIV_MYSLEL_ZE_PRASKLA_TA_PORPORCENA_PONCE_PORCELANOVA_POLCELANOVA_PORCENALOVA_PONCELAR_JAK_SE_TO_HONEM_TO_BILE_VITE_IZOLATOR_JAK_SE_TO_JMENUJE_KREMICITAN_HLINITY_PORCELAN_PIKSLA_JA_MYSLEL_ZE_PRASKLA_TA_PIKSLA_SE_VSIM_VSUDY_TAK_ROZSKRTNU_SIRKU_A_ONA_TAM_JE_CELA_ONA_JE_CELA_A_JA_JAKO_SLOUP_AZ_MNE_SIRKA_SPALILA_PRSTY_A_PRYC_PRES_POLE_POTME_NA_BREVNOV_NEBO_DO_STRESOVIC_AA_NEKDE_ME_NAPADLO_TO_SLOVO_KRAKATOE_KRAKATIT_KRAKATIT_NE_TAK_TO_NENENEBYLO_JAK_TO_BOUCHLO_LETIM_NA_ZEM_A_KRICIM_KRAKATIT_KRAKATIT_PAK_JSEM_NA_TO_ZAPOMNEL_KDO_JE_TU_KDO_KDO_JSTE_KOLEGA_TOMES_TOMES_AHA_TEN_VSIVAK_PREDNASKY_SI_VYPUJCOVAL_NEVRATIL_MNE_JEDEN_SESIT_CHEMIE_TOMES_JAK_SE_JMENOVAL_JIRI_JA_UZ_VIM_JIRKA_TY_JSI_JIRKA_JA_VIM_JIRKA_TOMES_KDE_MAS_TEN_SESIT_POCKEJ_JA_TI_NECO_REKNU_AZ_VYLETI_TO_OSTATNI_JE_ZLE_CLOVECE_TO_ROZMLATI_CELOU_PRAHU_SMETE_ODFOUKNE_FT_AZ_VYLETI_TA_PORCELANOVA_DOZE_VIS_JAKA_DOZE_TY_JSI_JIRKA_TOMES_JA_VIM_JDI_DO_KARLINA_DO_KARLINA_NEBO_DO_VYSOCAN_A_DIVEJ_SE_AZ_TO_VYLETI_BEZ_BEZ_HONEM_PROC_JA_TOHO_NADELAL_CENT_CENT_KRAKATITU_NE_ASI_ASI_PATNACT_DEKA_TAM_NAHORE_V_TE_PORCELANOVE_DOZI_CLOVECE_AZ_TA_VYLETI_ALE_POCKEJ_TO_NENI_MOZNE_TO_JE_NESMYSL_MUMLAL_PROKOP_CHYTAJE_SE_ZA_HLAVU_NU_PROC_PROC_PROC_TO_NEVYBOUCHLO_TAKE_V_TE_DOZI_KDYZ_TEN_PRASEK_SAM_OD_SEBE_POCKEJ_NA_STOLE_JE_ZINZINKOVY_PLECH_PLECH_OD_CEHO_TO_NA_STOLE_VYBUCHLO_POCKEJ_BUD_TISE_BUD_TISE_DRTIL_PROKOP_A_VRAVORAVE_SE_ZVEDL_CO_JE_TI_KRAKATIT_ZABRUCEL_PROKOP_UDELAL_CELYM_TELEM_JAKYSI_OTACIVY_POHYB_A_SVALIL_SE_NA_ZEM_V_MRAKOTACH___KRAKATIT_KAREL_CAPEK_I_II_III_UDAJE_O_TEXTU_TITULEK_KRAKATIT_PODTITULEK_II_AUTOR_KAREL_CAPEK_KRATKY_POPIS_UTOPISTICKY_ROMAN_O_OBJEVU_TRASKAVINY_NEPREDSTAVITELNE_SILY_VYDANY_POPRVE_V_R_ZDROJ_CAPEK_KAREL_TOVARNA_NA_ABSOLUTNO_KRAKATIT_MESTSKA_KNIHOVNA_V_PRAZE_PDF_LICENCE_PD_OLD_CASOP_LIDOVE_NOVINY_O_STORCHMARIEN_PRVNI_CO_SI_PROKOP_UVEDOMIL_BYLO_ZE_SE_S_NIM_VSECHNO_OTRASA_V_DRNCIVEM_RACHOTU_A_ZE_HO_NEKDO_PEVNE_DRZI_KOLEM_PASU_HROZNE_SE_BAL_OTEVRITI_OCI_MYSLEL_ZE_SE_TO_NA_NEJ_RITI_ALE_KDYZ_TO_NEUSTAVALO_OTEVREL_OCI_A_VIDEL_PRED_SEBOU_MATNY_CTYRUHELNIK_KTERYM_SE_SUNOU_MLHAVE_SVETELNE_KOULE_A_PRUHY_NEUMEL_SI_TO_VYSVETLIT_DIVAL_SE_ZMATENE_NA_UPLYVAJICI_A_POSKAKUJICI_MATOHY_TRPNE_ODEVZDAN_VE_VSE_CO_SE_S_NIM_BUDE_DIT_PAK_POCHOPIL_ZE_TEN_HORLIVY_RACHOT_JSOU_KOLA_VOZU_A_VENKU_ZE_MIJEJI_JENOM_SVITILNY_V_MLZE_A_UNAVEN_TOLIKERYM_POZOROVANIM_ZAVREL_OPET_OCI_A_NECHAL_SE_UNASET_TED_SI_LEHNES_REKL_TISE_HLAS_NAD_JEHO_HLAVOU_SPOLKNES_ASPIRIN_A_BUDE_TI_LIP_RANO_TI_PRIVEDU_DOKTORA_ANO_KDO_JE_TO_PTAL_SE_PROKOP_OSPALE_TOMES_LEHNES_SI_U_MNE_PROKOPE_MAS_HORECKU_KDE_TE_TO_BOLI_VSUDE_HLAVA_SE_MI_TOCI_TAK_VIS_JEN_TISE_LEZ_VARIM_TI_CAJ_A_VYSPIS_SE_MAS_TO_Z_ROZCILENI_VIS_TO_JE_TAKOVA_NERVOVA_HORECKA_DO_RANA_TO_PREJDE_PROKOP_SVRASTIL_CELO_V_NAMAZE_VZPOMINANI_JA_VIM_REKL_PO_CHVILI_STAROSTLIVE_POSLYS_ALE_NEKDO_BY_MEL_TU_PIKSLU_HODIT_DO_VODY_ABY_NEVYBOUCHLA_BEZ_STAROSTI_TED_NEMLUV_A_JA_BYCH_SNAD_MOHL_SEDET_NEJSEM_TI_TEZKY_NE_JEN_LEZ_A_TY_MAS_TEN_MUJ_SESIT_CHEMIE_VZPOMNEL_SI_PROKOP_NAJEDNOU_ANO_DOSTANES_JEJ_ALE_TED_KLID_SLYSIS_JA_TI_MAM_TAK_TEZKOU_HLAVU_ZATIM_DRKOTALA_DROZKA_NAHORU_JECNOU_ULICI_TOMES_SLABOUNCE_HVIZDAL_NEJAKOU_MELODII_A_DIVAL_SE_OKNEM_PROKOP_SIPAVE_DYCHAL_S_TICHYM_STENANIM_MLHA_SMACELA_CHODNIKY_A_VNIKALA_AZ_POD_KABAT_SVYM_SYCHRAVYM_SLIZEM_BYLO_PUSTO_A_POZDE_UZ_TAM_BUDEME_REKL_TOMES_NAHLAS_DROZKA_SE_CERSTVEJI_ROZHRCELA_NA_NAMESTI_A_ZAHNULA_VPRAVO_POCKEJ_PROKOPE_MUZES_UDELAT_PAR_KROKU_JA_TI_POMOHU_S_NAMAHOU_VLEKL_TOMES_SVEHO_HOSTA_DO_DRUHEHO_PATRA_PROKOP_SI_PRIPADAL_JAKSI_LEHKY_A_BEZ_VAHY_A_NECHAL_SE_SKORO_VYNEST_PO_SCHODECH_NAHORU_ALE_TOMES_SILNE_ODDECHOVAL_A_UTIRAL_SI_POT_VID_JSEM_JAKO_NITE_DIVIL_SE_PROKOP_NU_OVSEM_MRUCEL_UDYCHANY_TOMES_ODEMYKAJE_SVUJ_BYT_PROKOPOVI_BYLO_JAKO_MALEMU_DITETI_KDYZ_JEJ_TOMES_SVLEKAL_MA_MAMINKA_ZACAL_NECO_POVIDAT_KDYZ_MA_MAMINKA_TO_UZ_JE_TO_UZ_JE_DAVNO_TATINEK_SEDEL_U_STOLU_A_MAMINKA_MNE_NOSILA_DO_POSTELE_ROZUMIS_PAK_UZ_BYL_V_POSTELI_PRIKRYT_PO_BRADU_JEKTAL_ZUBY_A_DIVAL_SE_JAK_SE_TOMES_TOCI_U_KAMEN_A_RYCHLE_ZATAPI_BYLO_MU_DO_PLACE_DOJETIM_LITOSTI_A_SLABOSTI_A_PORAD_BREBENTIL_UKLIDNIL_SE_AZ_DOSTAL_NA_CELO_STUDENY_OBKLADEK_TU_SE_TISE_DIVAL_PO_POKOJI_BYLO_TU_CITIT_TABAK_A_ZENU_TY_JSI_KUJON_TOMSI_OZVAL_SE_VAZNE_PORAD_MAS_HOLKY_TOMES_SE_K_NEMU_OBRATIL_NU_A_CO_NIC_CO_VLASTNE_DELAS_TOMES_MAVL_RUKOU_MIZERNE_KAMARADE_PENIZE_NEJSOU_FLAMUJES_TOMES_JEN_POTRASL_HLAVOU_A_JE_TE_SKODA_VIS_ZACAL_PROKOP_STAROSTLIVE_TY_BYS_MOHL_KOUKEJ_JA_DELAM_UZ_DVANACT_LET_A_CO_Z_TOHO_MAS_NAMITL_TOMES_PRIKRE_NO_SEM_TAM_NECO_PRODAL_JSEM_LETOS_TRASKAVY_DEXTRIN_ZAC_ZA_DESET_TISIC_VIS_NIC_TO_NENI_HLOUPOST_TAKOVA_PITOMA_BOUCHACKA_PRO_DOLY_ALE_KDYBYCH_CHTEL_JE_TI_UZ_LIP_KRASNE_MI_JE_JA_JSEM_TI_NASEL_METODY_CLOVECE_JEDEN_NITRATCERU_TO_TI_JE_VASNIVA_POTVORA_A_CHLOR_TETRASTUPEN_CHLORDUSIKU_SE_ZAPALI_SVETLEM_ROZSVITIS_ZAROVKU_A_PRASK_ALE_TO_NIC_NENI_KOUKEJ_PROHLASIL_NAHLE_VYSTRKUJE_ZPOD_POKRYVKY_HUBENOU_DESNE_ZKOMOLENOU_RUKU_KDYZ_NECO_VEZMU_DO_RUKY_TAK_V_TOM_CITIM_SUMET_ATOMY_ZROVNA_TO_MRAVENCI_KAZDA_HMOTA_MRAVENCI_JINAK_ROZUMIS_NE_TO_JE_SILA_VIS_SILA_V_HMOTE_HMOTA_JE_STRASNE_SILNA_JA_JA_HMATAM_JAK_SE_TO_V_NI_HEMZI_DRZI_TO_DOHROMADY_S_HROZNOU_NAMAHOU_JAK_TO_UVNITR_ROZVIKLAS_ROZPADNE_SE_BUM_VSECHNO_JE_EXPLOZE_KDYZ_SE_ROZEVRE_KVETINA_JE_TO_EXPLOZE_KAZDA_MYSLENKA_TO_JE_TAKOVE_PRASKNUTI_V_MOZKU_KDYZ_MNE_PODAS_RUKU_CITIM_JAK_V_TOBE_NECO_EXPLODUJE_JA_MAM_TAKOVY_HMAT_CLOVECE_A_SLUCH_VSECHNO_SUMI_JAKO_SUMIVY_PRASEK_TO_JSOU_SAME_MALINKATE_VYBUCHY_MNE_TI_TAK_HUCI_V_HLAVE_RATATATA_JAKO_STROJNI_PUSKA_TAK_REKL_TOMES_A_TED_SPOLKNI_TUHLETEN_ASPIRIN_ANO_TRETRASKAVY_ASPIRIN_PERCHLOROVANY_ACETYLSALICYLAZID_TO_NIC_NENI_CLOVECE_JA_JSEM_NASEL_EXOTERMICKE_TRASKAVINY_KAZDA_LATKA_JE_VLASTNE_TRASKAVINA_VODA_VODA_JE_TRASKAVINA_HLINA_A_VZDUCH_JSOU_TRASKAVINY_PERI_PERI_V_PERINE_JE_TAKY_TRASKAVINA_VIS_ZATIM_TO_MA_JEN_TEORETICKY_VYZNAM_A_JA_JSEM_NASEL_ATOMOVE_VYBUCHY_JA_JA_JA_JSEM_UDELAL_ALFAEXPLOZE_ROZPADNE_SE_TO_NA_PLUS_PLUS_CASTICE_ZADNA_TERMOCHEMIE_DESTRUKCE_DESTRUKTIVNI_CHEMIE_CLOVECE_TO_TI_JE_OHROMNA_VEC_TOMSI_CISTE_VEDECKY_JA_TI_MAM_DOMA_TABULKY_LIDI_KDYBYCH_JA_MEL_APARATY_ALE_JA_MAM_JEN_OCI_A_RUCE_POCKEJ_AZ_TO_NAPISU_NECHCE_SE_TI_SPAT_CHCE_JSEM_DNES_UNAVEN_A_CO_TYS_PORAD_DELAL_NU_NIC_ZIVOT_ZIVOT_JE_TRASKAVINA_VIS_PRASK_CLOVEK_SE_NARODI_A_ROZPADNE_SE_BUM_A_NAM_SE_ZDA_ZE_TO_TRVA_BUHVIKOLIK_LET_VID_POCKEJ_JA_JSEM_TED_NECO_SPLETL_ZE_DOCELA_V_PORADKU_PROKOPE_MOZNA_ZE_ZITRA_UDELAM_BUM_NEBUDULI_MIT_TOTIZ_PENIZE_ALE_TO_JE_JEDNO_STAROUSI_JEN_SPI_JA_BYCH_TI_PUJCIL_NECHCES_NECH_NA_TO_BYS_NESTACIL_SNAD_JESTE_MUJ_TATIK_TOMES_MAVL_RUKOU_TAK_VIDIS_TY_MAS_JESTE_TATINKA_OZVAL_SE_PROKOP_PO_CHVILI_S_NAHLOU_MEKKOSTI_NU_ANO_DOKTOR_V_TYNICI_TOMES_VSTAL_A_PRECHAZEL_PO_POKOJI_JE_TO_MIZERIE_CLOVECE_MIZERIE_MAM_TO_NAHNUTE_NU_A_NESTAREJ_SE_O_MNE_JA_UZ_NECO_UDELAM_SPI_PROKOP_SE_UTISIL_POLOZAVRENYMA_OCIMA_VIDEL_JAK_TOMES"
    
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