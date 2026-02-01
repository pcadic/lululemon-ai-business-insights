import pandas as pd
from transformers import pipeline
import os

INPUT = "data/processed/sentiment_enriched.csv"
OUTPUT = "data/processed/topic_enriched.csv"

os.environ["HF_TOKEN"] = "HF_TOKEN"

TOPICS = [
    "Product quality",
    "Pricing",
    "Customer service",
    "Store experience",
    "Size & Fit",
    "Inventory & Stock",
    "Staff Knowledge"
]

def main():
    if not os.path.exists(INPUT):
        print(f"❌ Erreur : Le fichier {INPUT} n'existe pas.")
        return

    df = pd.read_csv(INPUT)
    if df.empty:
        print("⚠️ Le fichier est vide.")
        return

    print(f"🤖 Chargement du modèle Zero-Shot Classification (BART)...")
    # Utilisation d'un modèle puissant pour la classification thématique
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    print(f"⏳ Classification de {len(df)} avis en cours...")
    
    # Nettoyage et préparation des textes (tronqués à 512 caractères pour la performance)
    texts = df['text'].fillna("").apply(lambda x: str(x)[:512]).tolist()

    try:
        # Classification par lot (plus rapide que .apply)
        results = classifier(texts, candidate_labels=TOPICS, multi_label=False)
        
        # Extraction du label avec le score le plus élevé pour chaque texte
        df['topic'] = [res['labels'][0] for res in results]
        df['topic_score'] = [res['scores'][0] for res in results]

    except Exception as e:
        print(f"❌ Erreur lors de la classification : {e}")
        return

    # Sauvegarde
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"✅ Classification terminée. Fichier sauvegardé : {OUTPUT}")

if __name__ == "__main__":
    main()
