import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    probabilities = np.linspace(0.001, 0.999, 500)
    entropy = -probabilities * np.log2(probabilities) - (1 - probabilities) * np.log2(
        1 - probabilities
    )

    plt.figure(figsize=(6, 4))
    plt.plot(probabilities, entropy, color="#1f77b4", linewidth=2)
    plt.axvline(0.5, color="#ff7f0e", linestyle="--", linewidth=1)
    plt.axhline(1.0, color="#2ca02c", linestyle=":", linewidth=1)
    plt.text(
        0.52,
        1.00,
        "Maximum entropy at 1 bit/symbol",
        fontsize=9,
        color="#2ca02c",
    )

    plt.title("Shannon's First Theorem: Binary Source Entropy")
    plt.xlabel("Probability of symbol '1'")
    plt.ylabel("Entropy (bits per symbol)")
    plt.grid(alpha=0.3, linestyle=":")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
