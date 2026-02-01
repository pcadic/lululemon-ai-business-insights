import pandas as pd
from transformers import pipeline
import os

# Chemins de fichiers
INPUT = "data/raw/reviews_raw.csv"
OUTPUT = "data/processed/sentiment_enriched.csv"

def main():
    # 1. Chargement des données
    if not os.path.exists(INPUT):
        print(f"❌ Erreur : Le fichier {INPUT} n'existe pas.")
        return
        
    df = pd.read_csv(INPUT)
    if df.empty:
        print("⚠️ Le fichier d'entrée est vide.")
        return

    print(f"🤖 Chargement du modèle de sentiment (Multilingue)...")
    # Utilisation d'un modèle plus robuste pour les avis (1 à 5 étoiles)
    # On le charge UNE SEULE FOIS ici
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    sentiment_pipeline = pipeline("sentiment-analysis", model=model_name)

    def analyze_sentiment(text):
        if pd.isna(text) or text.strip() == "":
            return "NEUTRAL", 0.0
        
        # Le modèle BERT a une limite de 512 tokens
        result = sentiment_pipeline(text[:512])[0]
        
        # Le modèle nlptown renvoie des labels type "1 star", "2 stars", etc.
        # On convertit cela en POSITIVE / NEGATIVE pour ton app Streamlit
        stars = int(result['label'].split()[0])
        
        if stars >= 4:
            label = "POSITIVE"
        elif stars <= 2:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"
            
        return label, result['score']

    print(f"⏳ Analyse de {len(df)} avis en cours...")
    
    # Application de l'analyse (plus rapide ainsi)
    results = df['text'].apply(analyze_sentiment)
    
    # Séparation des résultats en deux colonnes
    df[['sentiment', 'sentiment_score']] = pd.DataFrame(results.tolist(), index=df.index)

    # 3. Sauvegarde
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"✅ Analyse terminée. Fichier sauvegardé dans : {OUTPUT}")

if __name__ == "__main__":
    main()
