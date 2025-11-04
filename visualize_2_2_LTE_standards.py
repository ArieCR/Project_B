import matplotlib.pyplot as plt


def main() -> None:
    bandwidths_mhz = [1.4, 3, 5, 10, 15, 20]
    resource_blocks = [6, 15, 25, 50, 75, 100]

    plt.figure(figsize=(6, 4))
    bars = plt.bar(bandwidths_mhz, resource_blocks, width=0.6, color="#1f77b4")
    for bar, rb in zip(bars, resource_blocks):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{rb} RBs", ha="center", va="bottom", fontsize=9)

    plt.title("LTE Transmission Bandwidth Configuration")
    plt.xlabel("Channel Bandwidth (MHz)")
    plt.ylabel("Maximum Resource Blocks")
    plt.grid(axis="y", alpha=0.3, linestyle=":")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
