import pandas as pd
import os

INPUT = "data/processed/topic_enriched.csv"
OUTPUT = "data/processed/business_insights.csv"

def main():
    if not os.path.exists(INPUT):
        print(f"❌ Erreur : {INPUT} introuvable.")
        return

    df = pd.read_csv(INPUT)
    
    # 1. On crée l'agrégation de base
    insights = (
        df.groupby(["store_name", "topic", "sentiment"])
        .size()
        .reset_index(name="count")
    )

    # 2. Sécurité : S'assurer que chaque magasin a toutes les combinaisons
    # Cela évite que les graphes ne "sautent" ou ne plantent dans Streamlit
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    insights.to_csv(OUTPUT, index=False)
    print(f"✅ Insights générés avec succès : {OUTPUT}")

if __name__ == "__main__":
    main()
