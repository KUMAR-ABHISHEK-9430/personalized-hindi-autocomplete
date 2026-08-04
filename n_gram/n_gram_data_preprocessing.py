import re

def fix_eod_boundaries(raw_text:str)-> str:
    """
    Cleans up and strictly enforces <eod> document boundaries based on templates.
    """
    # 1. First, wipe out any existing <eod> tags to start with a clean slate
    raw_text = raw_text.replace('<eod>', '')
    
    # 2. Standardize common misspellings that break regex
    raw_text = re.sub(r'सेंवा\s*में', 'सेवा में', raw_text)
    raw_text = re.sub(r'मोहनियाॅ', 'मोहनिया', raw_text)
    raw_text = re.sub(r'मोहनियॉ', 'मोहनिया', raw_text)
    
    # 3. Add <eod> AFTER the signature block
    # Looks for: पु0अ0नि0 -> मोहनियां थाना -> कैमूर । (with flexible spacing/newlines)
    sig_pattern = r'(पु0\s*अ0\s*नि0\s*\n\s*मोहनिया\s*थाना\s*\n\s*कैमूर\s*।)'
    raw_text = re.sub(sig_pattern, r'\1\n<eod>\n', raw_text)
    
    # 4. Add <eod> BEFORE Gyapank block
    raw_text = re.sub(r'(ज्ञापांक-\s*मोहनिया\s*थाना)', r'\n<eod>\n\1', raw_text)
    
    # 5. Add <eod> BEFORE 'सेवा में'
    raw_text = re.sub(r'(सेवा\s*में)', r'\n<eod>\n\1', raw_text)
    
    # 6. FIX THE COLLISION: 
    # If we added <eod> before Gyapank AND <eod> before Sewa me, we remove the one before Sewa me.
    # Matches: <eod> -> Gyapank line -> Date line -> <eod> -> Sewa me
    collision_pattern = r'(<eod>\nज्ञापांक-[^\n]*\n\s*दिनांक-[^\n]*\n)\s*<eod>\n(सेवा\s*में)'
    raw_text = re.sub(collision_pattern, r'\1\2', raw_text)
    
    # Clean up massive chunks of empty lines caused by our replacements
    raw_text = re.sub(r'\n{3,}', '\n\n', raw_text)
    
    return raw_text


def preprocess_police_data(raw_text:str)-> list:
    """
    Preprocesses raw data for n-gram model training.
    """
    # Enforce strict document boundaries
    raw_text = fix_eod_boundaries(raw_text)
    
    # Split into documents using the newly fixed <eod> tag
    documents = raw_text.split("<eod>")
    
    processed_sentences = []
    
    for doc in documents:
        doc = doc.strip()
        if not doc:
            continue
            
        # --- Variable Masking (The "Regex NER" Engine) ---
        
        # FIR No: e.g., कांड संख्या-XXXX/YY
        doc = re.sub(r'कांड संख्,?या\s*-\s*\d+/\d+', 'कांड संख्या-<FIR_NUM>', doc)
        
        # Bank Account: खाता संख्या-1234567890
        doc = re.sub(r'खाता संख्या-\d+', 'खाता संख्या-<ACCOUNT_NUM>', doc)
        
        # Victim/Deceased Name (Between identifier and age/father/husband)
        doc = re.sub(r'(पिड़ीता|पीड़ीता|पीड़ीत|पिड़ता|मृत्का|मृतिका|पत्नी)\s+(.*?)\s+(उम्र|पिता|पति|पे0)', r'\1 <NAME> \3', doc)
        
        # Accused/Complainant Name (Between identifier and father)
        doc = re.sub(r'(अभियुक्त|धारक|वादी)\s+(.*?)\s+(पिता|पे0)', r'\1 <NAME> \3', doc)
        
        # Father/Husband Name (Between relation identifier and alias/village)
        doc = re.sub(r'(पे0|पिता|पति)\s+(.*?)\s+(उर्फ|सा0|ग्राम)', r'\1 <NAME> \3', doc)
        
        # Alias
        doc = re.sub(r'उर्फ\s+(.*?)\s+सा0', 'उर्फ <NAME> सा0', doc)
        
        # Village / Gram (Handles 'सा0-' or 'ग्राम ')
        doc = re.sub(r'(सा0-|ग्राम\s+)(.*?)\s+(थाना|पो0)', r'\1<VILLAGE> \3', doc)
        
        # Age
        doc = re.sub(r'उम्र करीब-?\s*\d+', 'उम्र करीब-<AGE>', doc)
        
        # Sections (Dhara): Matches complex formats like 115(2)/126(2)/74
        doc = re.sub(r'धारा-[\w\d\(\)/]+', 'धारा-<SECTIONS>', doc)
        
        # Phone numbers
        doc = re.sub(r'मो0न0-\d+', 'मो0न0-<PHONE>', doc)


        # --- Standardization & Punctuation ---
        
        # Fix the spacing issue with "पु0अ0नि0"
        doc = re.sub(r'पु0\s*अ0\s*नि0', 'पु0अ0नि0', doc)
        
        # Add spaces around punctuation so they become separate tokens.
        # Included brackets and slashes for complex legal clauses.
        doc = re.sub(r'([,.:\-()|/])', r' \1 ', doc)
        
        # Remove extra white spaces caused by regex replacements
        doc = re.sub(r'\s+', ' ', doc)
        
        
        # --- Tokenization and Padding (Line by Line) ---
        lines = doc.split('\n')
        
        for line in lines:
            line = line.strip()
            if line:
                # Add padding for a Trigram model (n=3 requires two start tags)
                padded_line = f"<s> <s> {line} </s>"
                processed_sentences.append(padded_line)
                
    return processed_sentences

# --- Execution Example ---
if __name__ == "__main__":
    # Load your raw text here (we are using a small snippet for testing)
    sample_text = """
    ज्ञापांक- मोहनियॉ थाना का कार्यालय
    दिनांक-
    सेंवा में,
    माननीय अपर मुख्य न्यायिक दण्डाधिकारी ,प्रथम , महोदय
    मोहनियॉ (कैमूर)
    प्रसंग :- मोहनियाॅ थाना कांड संख्,या-400/20 दिनांक-<DATE> धारा-420/468/379 भा0द0वि0
    विषय :- बारंट निर्गत करने के संबंध में अनुरोध -पत्र ।
    महाशय्
    उपयुर्क्त प्रसंगाधीन विषय के संदर्भ में सादर सूचित करना हैं कि प्रासांगीक कांड के प्राथमिकी नामजद अभियुक्त खाता संख्या-2 के धारक  कुमार  सा0-किशनपुर बलौर थाना-कुढ़नी जिला- गिरफ्फतारी के भय से भागे फिर रहें हैं ।
    पु0 अ0 नि0
    थाना
    कैमूर ।
    """
    
    processed = preprocess_police_data(sample_text)
    
    print("Processed Sentences Ready for N-Gram Training:\n")
    for s in processed:
        print(s)

