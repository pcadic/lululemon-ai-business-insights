import os
import pandas as pd
from datetime import datetime

# -----------------------------
# Configuration
# -----------------------------
OUTPUT_DIR = "data/raw"
OUTPUT_FILE = "texts.csv"

# -----------------------------
# Sample real business texts
# (stand-in for public sources)
# -----------------------------
TEXT_SOURCES = [
    {
        "source": "Investor Communication",
        "title": "Lululemon Q3 Earnings Call",
        "text": (
            "Lululemon reported strong revenue growth driven by continued demand "
            "for its core apparel categories. The company highlighted progress "
            "in supply chain optimization and sustainability initiatives, while "
            "acknowledging pricing pressures and increased competition."
        ),
    },
    {
        "source": "Press Release",
        "title": "Lululemon Sustainability Update",
        "text": (
            "Lululemon reaffirmed its commitment to sustainable materials and "
            "responsible sourcing. Investments in recycled fabrics and reduced "
            "carbon emissions remain central to the brand’s long-term strategy."
        ),
    },
    {
        "source": "Brand Statement",
        "title": "Customer Experience Focus",
        "text": (
            "Enhancing the in-store and digital customer experience continues to "
            "be a priority. Lululemon is investing in store innovation, employee "
            "training, and community engagement."
        ),
    },
]

# -----------------------------
# Main logic
# -----------------------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    records = []
    for item in TEXT_SOURCES:
        records.append(
            {
                "date": datetime.utcnow().date(),
                "source": item["source"],
                "title": item["title"],
                "text": item["text"],
            }
        )

    df = pd.DataFrame(records)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df.to_csv(output_path, index=False)

    print(f"Saved {len(df)} texts to {output_path}")


if __name__ == "__main__":
    main()
