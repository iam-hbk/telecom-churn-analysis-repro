"""Consumer Analytics Assignment - Reproducible Python Script.

This script keeps dependencies to the Python standard library only.
It currently implements the sentiment-analysis section outputs:

1) Overall sentiment distribution
2) Negative sentiment by Gender
3) Negative sentiment by TechSupport

Generated artifacts:
- tables/*.csv
- figures/*.svg
"""

from __future__ import annotations

import csv
import math
import random
import re
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape


# Project paths (kept explicit for easy reproducibility)
ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "telecom_churn_sentiment.csv"
FIGURES_DIR = ROOT / "figures"
TABLES_DIR = ROOT / "tables"


def load_rows(path: Path) -> list[dict[str, str]]:
    """Load CSV rows as dictionaries with UTF-8 decoding."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def preview_dataset(rows: list[dict[str, str]]) -> None:
    """Print a small dataset preview for quick validation."""
    print(f"Total rows: {len(rows)}")
    if rows:
        print(f"Columns: {list(rows[0].keys())}")


def ensure_output_dirs() -> None:
    """Create output folders used for report artifacts."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)


def clean_value(value: str | None) -> str:
    """Normalize empty grouping values to a readable label."""
    if value is None:
        return "Unknown"
    text = value.strip()
    return text if text else "Unknown"


def count_values(rows: list[dict[str, str]], column: str) -> Counter[str]:
    """Count values in a column."""
    return Counter(clean_value(row.get(column)) for row in rows)


def compute_group_negative_rates(
    rows: list[dict[str, str]],
    group_col: str,
    sentiment_col: str = "Sentiment",
) -> list[dict[str, str]]:
    """Compute negative count and rate by group."""
    totals = Counter()
    negatives = Counter()

    for row in rows:
        group = clean_value(row.get(group_col))
        totals[group] += 1
        sentiment = clean_value(row.get(sentiment_col)).lower()
        if sentiment == "negative":
            negatives[group] += 1

    output: list[dict[str, str]] = []
    for group, total in totals.items():
        neg = negatives[group]
        rate = (neg / total) * 100 if total else 0.0
        output.append(
            {
                "group": group,
                "negative_count": str(neg),
                "total_count": str(total),
                "negative_rate_percent": f"{rate:.2f}",
            }
        )

    output.sort(key=lambda x: float(x["negative_rate_percent"]), reverse=True)
    return output


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    """Write list-of-dict rows to CSV."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_bar_chart_svg(
    path: Path,
    title: str,
    x_label: str,
    y_label: str,
    categories: list[str],
    values: list[float],
    value_suffix: str = "",
    color: str = "#2E5AAC",
) -> None:
    """Create a simple, dependency-free SVG bar chart."""
    width = 980
    height = 620
    left = 90
    right = 40
    top = 90
    bottom = 120
    chart_w = width - left - right
    chart_h = height - top - bottom

    max_v = max(values) if values else 1.0
    if max_v <= 0:
        max_v = 1.0

    bar_area_w = chart_w / max(len(categories), 1)
    bar_w = min(70, bar_area_w * 0.55)

    lines = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>",
        "<rect width='100%' height='100%' fill='white' />",
        f"<text x='{width / 2}' y='42' text-anchor='middle' font-size='24' font-family='Arial' fill='#222'>{escape(title)}</text>",
        f"<line x1='{left}' y1='{top + chart_h}' x2='{left + chart_w}' y2='{top + chart_h}' stroke='#444' stroke-width='2' />",
        f"<line x1='{left}' y1='{top}' x2='{left}' y2='{top + chart_h}' stroke='#444' stroke-width='2' />",
    ]

    # Y-axis ticks (0 to max, 5 steps)
    steps = 5
    for i in range(steps + 1):
        y_val = max_v * i / steps
        y = top + chart_h - (chart_h * i / steps)
        lines.append(
            f"<line x1='{left - 6}' y1='{y:.1f}' x2='{left}' y2='{y:.1f}' stroke='#444' stroke-width='1' />"
        )
        lines.append(
            f"<text x='{left - 12}' y='{y + 4:.1f}' text-anchor='end' font-size='12' font-family='Arial' fill='#333'>{y_val:.1f}</text>"
        )
        lines.append(
            f"<line x1='{left}' y1='{y:.1f}' x2='{left + chart_w}' y2='{y:.1f}' stroke='#E6E6E6' stroke-width='1' />"
        )

    for idx, (cat, val) in enumerate(zip(categories, values)):
        x_center = left + (idx + 0.5) * bar_area_w
        bar_h = (val / max_v) * chart_h
        y_top = top + chart_h - bar_h
        x_left = x_center - bar_w / 2

        lines.append(
            f"<rect x='{x_left:.1f}' y='{y_top:.1f}' width='{bar_w:.1f}' height='{bar_h:.1f}' fill='{color}' />"
        )
        lines.append(
            f"<text x='{x_center:.1f}' y='{y_top - 8:.1f}' text-anchor='middle' font-size='12' font-family='Arial' fill='#111'>{val:.2f}{escape(value_suffix)}</text>"
        )
        lines.append(
            f"<text x='{x_center:.1f}' y='{top + chart_h + 22}' text-anchor='middle' font-size='12' font-family='Arial' fill='#222'>{escape(cat)}</text>"
        )

    lines.append(
        f"<text x='{width / 2}' y='{height - 36}' text-anchor='middle' font-size='14' font-family='Arial' fill='#222'>{escape(x_label)}</text>"
    )
    # Vertical y-label (rotated)
    lines.append(
        f"<text x='24' y='{height / 2}' transform='rotate(-90 24 {height / 2})' text-anchor='middle' font-size='14' font-family='Arial' fill='#222'>{escape(y_label)}</text>"
    )

    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_sentiment_outputs(rows: list[dict[str, str]]) -> None:
    """Build sentiment tables and charts for report Section 3."""
    sentiment_counts = count_values(rows, "Sentiment")
    total = len(rows)

    sentiment_rows: list[dict[str, str]] = []
    for label, count in sentiment_counts.items():
        sentiment_rows.append(
            {
                "sentiment": label,
                "count": str(count),
                "percent": f"{(count / total) * 100:.2f}",
            }
        )
    sentiment_rows.sort(key=lambda x: int(x["count"]), reverse=True)

    write_csv(
        TABLES_DIR / "sentiment_distribution.csv",
        sentiment_rows,
        ["sentiment", "count", "percent"],
    )

    save_bar_chart_svg(
        path=FIGURES_DIR / "sentiment_distribution.svg",
        title="Overall Sentiment Distribution",
        x_label="Sentiment",
        y_label="Count",
        categories=[r["sentiment"] for r in sentiment_rows],
        values=[float(r["count"]) for r in sentiment_rows],
        color="#1E88E5",
    )

    gender_rows = compute_group_negative_rates(rows, "Gender")
    write_csv(
        TABLES_DIR / "negative_by_gender.csv",
        gender_rows,
        ["group", "negative_count", "total_count", "negative_rate_percent"],
    )

    save_bar_chart_svg(
        path=FIGURES_DIR / "negative_by_gender.svg",
        title="Negative Sentiment Rate by Gender",
        x_label="Gender",
        y_label="Negative sentiment rate (%)",
        categories=[r["group"] for r in gender_rows],
        values=[float(r["negative_rate_percent"]) for r in gender_rows],
        value_suffix="%",
        color="#EF6C00",
    )

    tech_rows = compute_group_negative_rates(rows, "TechSupport")
    write_csv(
        TABLES_DIR / "negative_by_techsupport.csv",
        tech_rows,
        ["group", "negative_count", "total_count", "negative_rate_percent"],
    )

    save_bar_chart_svg(
        path=FIGURES_DIR / "negative_by_techsupport.svg",
        title="Negative Sentiment Rate by Tech Support",
        x_label="TechSupport group",
        y_label="Negative sentiment rate (%)",
        categories=[r["group"] for r in tech_rows],
        values=[float(r["negative_rate_percent"]) for r in tech_rows],
        value_suffix="%",
        color="#43A047",
    )

    print("\nGenerated tables:")
    print(f"- {TABLES_DIR / 'sentiment_distribution.csv'}")
    print(f"- {TABLES_DIR / 'negative_by_gender.csv'}")
    print(f"- {TABLES_DIR / 'negative_by_techsupport.csv'}")

    print("\nGenerated figures:")
    print(f"- {FIGURES_DIR / 'sentiment_distribution.svg'}")
    print(f"- {FIGURES_DIR / 'negative_by_gender.svg'}")
    print(f"- {FIGURES_DIR / 'negative_by_techsupport.svg'}")


# Compact English stopword set for reproducible filtering.
STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "did",
    "do",
    "does",
    "doing",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "me",
    "more",
    "most",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "she",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "with",
    "would",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
}


def preprocess_text(text: str | None) -> list[str]:
    """Lowercase + word/punctuation tokenization + English stopword filtering."""
    if text is None:
        return []
    lowered = text.lower()
    tokens = re.findall(r"\w+|[^\w\s]", lowered)
    filtered: list[str] = []
    for token in tokens:
        if token.isalpha() and token in STOPWORDS:
            continue
        filtered.append(token)
    return filtered


def build_stratified_folds(
    rows: list[dict[str, str]],
    label_col: str,
    n_folds: int = 5,
    seed: int = 42,
) -> list[list[dict[str, str]]]:
    """Create stratified folds to mimic Test & Score cross-validation."""
    rng = random.Random(seed)
    buckets: dict[str, list[dict[str, str]]] = {}

    for row in rows:
        label = clean_value(row.get(label_col))
        buckets.setdefault(label, []).append(row)

    for label_rows in buckets.values():
        rng.shuffle(label_rows)

    folds: list[list[dict[str, str]]] = [[] for _ in range(n_folds)]
    for label_rows in buckets.values():
        for i, row in enumerate(label_rows):
            folds[i % n_folds].append(row)

    return folds


class MultinomialNBText:
    """Simple multinomial Naive Bayes for tokenized text classification."""

    def __init__(self) -> None:
        self.class_priors: dict[str, float] = {}
        self.word_counts: dict[str, Counter[str]] = {}
        self.class_token_totals: dict[str, int] = {}
        self.vocab: set[str] = set()
        self.class_labels: list[str] = []

    def fit(self, tokenized_docs: list[list[str]], labels: list[str]) -> None:
        class_doc_counts = Counter(labels)
        total_docs = len(labels)

        self.class_labels = sorted(class_doc_counts.keys())
        self.word_counts = {label: Counter() for label in self.class_labels}
        self.class_token_totals = {label: 0 for label in self.class_labels}

        for tokens, label in zip(tokenized_docs, labels):
            self.word_counts[label].update(tokens)
            self.class_token_totals[label] += len(tokens)
            self.vocab.update(tokens)

        n_classes = len(self.class_labels)
        self.class_priors = {
            label: (class_doc_counts[label] + 1) / (total_docs + n_classes)
            for label in self.class_labels
        }

    def predict_one(self, tokens: list[str]) -> str:
        if not self.class_labels:
            raise RuntimeError("Model has not been fitted.")

        vocab_size = max(len(self.vocab), 1)
        token_counts = Counter(tokens)
        best_label = self.class_labels[0]
        best_score = -float("inf")

        for label in self.class_labels:
            score = math.log(self.class_priors[label])
            denom = self.class_token_totals[label] + vocab_size
            counts = self.word_counts[label]

            for token, cnt in token_counts.items():
                num = counts[token] + 1
                score += cnt * math.log(num / denom)

            if score > best_score:
                best_score = score
                best_label = label

        return best_label


def compute_binary_metrics(
    y_true: list[str],
    y_pred: list[str],
    positive_label: str = "Yes",
) -> dict[str, float]:
    """Compute accuracy, precision, recall, F1 and confusion matrix values."""
    tp = tn = fp = fn = 0
    for actual, pred in zip(y_true, y_pred):
        actual_pos = actual == positive_label
        pred_pos = pred == positive_label
        if actual_pos and pred_pos:
            tp += 1
        elif (not actual_pos) and (not pred_pos):
            tn += 1
        elif (not actual_pos) and pred_pos:
            fp += 1
        else:
            fn += 1

    total = len(y_true)
    accuracy = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (
        (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": float(tp),
        "tn": float(tn),
        "fp": float(fp),
        "fn": float(fn),
    }


def save_confusion_matrix_svg(path: Path, tp: int, tn: int, fp: int, fn: int) -> None:
    """Create a simple 2x2 confusion matrix chart as SVG."""
    w, h = 760, 540
    x0, y0 = 180, 120
    cell = 140

    lines = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>",
        "<rect width='100%' height='100%' fill='white' />",
        "<text x='380' y='48' text-anchor='middle' font-size='24' font-family='Arial' fill='#222'>Confusion Matrix (Churn Prediction)</text>",
        "<text x='380' y='86' text-anchor='middle' font-size='14' font-family='Arial' fill='#444'>Positive class: Churn = Yes</text>",
        f"<rect x='{x0}' y='{y0}' width='{cell}' height='{cell}' fill='#C8E6C9' stroke='#333' />",
        f"<rect x='{x0 + cell}' y='{y0}' width='{cell}' height='{cell}' fill='#FFCDD2' stroke='#333' />",
        f"<rect x='{x0}' y='{y0 + cell}' width='{cell}' height='{cell}' fill='#FFCDD2' stroke='#333' />",
        f"<rect x='{x0 + cell}' y='{y0 + cell}' width='{cell}' height='{cell}' fill='#C8E6C9' stroke='#333' />",
        f"<text x='{x0 + cell / 2}' y='{y0 + cell / 2 - 8}' text-anchor='middle' font-size='16' font-family='Arial' fill='#111'>TP</text>",
        f"<text x='{x0 + cell / 2}' y='{y0 + cell / 2 + 18}' text-anchor='middle' font-size='22' font-family='Arial' fill='#111'>{tp}</text>",
        f"<text x='{x0 + cell + cell / 2}' y='{y0 + cell / 2 - 8}' text-anchor='middle' font-size='16' font-family='Arial' fill='#111'>FP</text>",
        f"<text x='{x0 + cell + cell / 2}' y='{y0 + cell / 2 + 18}' text-anchor='middle' font-size='22' font-family='Arial' fill='#111'>{fp}</text>",
        f"<text x='{x0 + cell / 2}' y='{y0 + cell + cell / 2 - 8}' text-anchor='middle' font-size='16' font-family='Arial' fill='#111'>FN</text>",
        f"<text x='{x0 + cell / 2}' y='{y0 + cell + cell / 2 + 18}' text-anchor='middle' font-size='22' font-family='Arial' fill='#111'>{fn}</text>",
        f"<text x='{x0 + cell + cell / 2}' y='{y0 + cell + cell / 2 - 8}' text-anchor='middle' font-size='16' font-family='Arial' fill='#111'>TN</text>",
        f"<text x='{x0 + cell + cell / 2}' y='{y0 + cell + cell / 2 + 18}' text-anchor='middle' font-size='22' font-family='Arial' fill='#111'>{tn}</text>",
        f"<text x='{x0 + cell}' y='{y0 - 22}' text-anchor='middle' font-size='14' font-family='Arial' fill='#222'>Predicted</text>",
        f"<text x='{x0 + cell / 2}' y='{y0 - 4}' text-anchor='middle' font-size='12' font-family='Arial' fill='#222'>Yes</text>",
        f"<text x='{x0 + cell + cell / 2}' y='{y0 - 4}' text-anchor='middle' font-size='12' font-family='Arial' fill='#222'>No</text>",
        f"<text x='{x0 - 70}' y='{y0 + cell}' text-anchor='middle' font-size='14' font-family='Arial' fill='#222' transform='rotate(-90 {x0 - 70} {y0 + cell})'>Actual</text>",
        f"<text x='{x0 - 12}' y='{y0 + cell / 2 + 4}' text-anchor='end' font-size='12' font-family='Arial' fill='#222'>Yes</text>",
        f"<text x='{x0 - 12}' y='{y0 + cell + cell / 2 + 4}' text-anchor='end' font-size='12' font-family='Arial' fill='#222'>No</text>",
        "</svg>",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")


def run_text_churn_model(rows: list[dict[str, str]], n_folds: int = 5) -> None:
    """Run cross-validated churn prediction from review text."""
    folds = build_stratified_folds(rows, label_col="Churn", n_folds=n_folds, seed=42)

    y_true_all: list[str] = []
    y_pred_all: list[str] = []

    for fold_idx in range(n_folds):
        test_rows = folds[fold_idx]
        train_rows: list[dict[str, str]] = []
        for idx, fold_rows in enumerate(folds):
            if idx != fold_idx:
                train_rows.extend(fold_rows)

        x_train = [preprocess_text(r.get("ReviewText")) for r in train_rows]
        y_train = [clean_value(r.get("Churn")) for r in train_rows]
        x_test = [preprocess_text(r.get("ReviewText")) for r in test_rows]
        y_test = [clean_value(r.get("Churn")) for r in test_rows]

        model = MultinomialNBText()
        model.fit(x_train, y_train)
        y_pred = [model.predict_one(tokens) for tokens in x_test]

        y_true_all.extend(y_test)
        y_pred_all.extend(y_pred)

    metrics = compute_binary_metrics(y_true_all, y_pred_all, positive_label="Yes")

    model_table = [
        {"metric": "accuracy", "value": f"{metrics['accuracy']:.4f}"},
        {"metric": "precision", "value": f"{metrics['precision']:.4f}"},
        {"metric": "recall", "value": f"{metrics['recall']:.4f}"},
        {"metric": "f1_score", "value": f"{metrics['f1']:.4f}"},
        {"metric": "tp", "value": str(int(metrics["tp"]))},
        {"metric": "fp", "value": str(int(metrics["fp"]))},
        {"metric": "fn", "value": str(int(metrics["fn"]))},
        {"metric": "tn", "value": str(int(metrics["tn"]))},
    ]

    write_csv(TABLES_DIR / "model_test_score.csv", model_table, ["metric", "value"])
    save_confusion_matrix_svg(
        FIGURES_DIR / "confusion_matrix.svg",
        tp=int(metrics["tp"]),
        tn=int(metrics["tn"]),
        fp=int(metrics["fp"]),
        fn=int(metrics["fn"]),
    )

    print("\nModel evaluation outputs:")
    print(f"- {TABLES_DIR / 'model_test_score.csv'}")
    print(f"- {FIGURES_DIR / 'confusion_matrix.svg'}")
    print(
        "Metrics: "
        f"accuracy={metrics['accuracy']:.4f}, "
        f"precision={metrics['precision']:.4f}, "
        f"recall={metrics['recall']:.4f}, "
        f"f1={metrics['f1']:.4f}"
    )


def main() -> None:
    # Step 1: verify data file is available before analysis.
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing expected dataset: {DATA_PATH}")

    # Load and preview dataset (foundation for all next steps).
    rows = load_rows(DATA_PATH)
    preview_dataset(rows)

    ensure_output_dirs()

    # Section 3 outputs: sentiment distributions and grouped negatives.
    generate_sentiment_outputs(rows)

    # Section 4 outputs: churn prediction Test & Score equivalent.
    run_text_churn_model(rows, n_folds=5)


if __name__ == "__main__":
    main()
