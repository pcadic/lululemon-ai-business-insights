import pandas as pd
from transformers import pipeline
import os

INPUT = "data/raw/reviews_raw.csv"
OUTPUT = "data/processed/sentiment_enriched.csv"

os.environ["HF_TOKEN"] = "HF_TOKEN"

def main():
    if not os.path.exists(INPUT):
        print(f"❌ Erreur : {INPUT} introuvable.")
        return

    df = pd.read_csv(INPUT)
    if df.empty:
        print("⚠️ Le fichier d'entrée est vide.")
        return

    print("🤖 Chargement du modèle de sentiment multilingue...")
    # Modèle spécialisé pour les avis (1 à 5 étoiles)
    model_id = "nlptown/bert-base-multilingual-uncased-sentiment"
    sentiment_task = pipeline("sentiment-analysis", model=model_id)

    def process_sentiment(text):
        if pd.isna(text) or text.strip() == "":
            return "NEUTRAL", 0.0
        
        # Troncature à 512 tokens pour éviter les crashs sur les avis longs
        result = sentiment_task(text[:512])[0]
        
        # Conversion du label "X stars" en sentiment binaire/neutre
        stars = int(result['label'].split()[0])
        if stars >= 4:
            label = "POSITIVE"
        elif stars <= 2:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"
            
        return label, result['score']

    print(f"⏳ Analyse de {len(df)} avis...")
    # On applique l'analyse
    results = df['text'].apply(process_sentiment)
    
    # On éclate les résultats en deux colonnes
    df[['sentiment', 'sentiment_score']] = pd.DataFrame(results.tolist(), index=df.index)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"✅ Sentiment terminé -> {OUTPUT}")

if __name__ == "__main__":
    main()
