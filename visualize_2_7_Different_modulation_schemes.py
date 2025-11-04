import numpy as np
import matplotlib.pyplot as plt


def calculate_papr(signal: np.ndarray) -> float:
    power = np.abs(signal) ** 2
    return np.max(power) / power.mean()


def simulate(trials: int = 200, n_subcarriers: int = 64, data_subcarriers: int = 12) -> tuple[np.ndarray, np.ndarray]:
    ofdm_papr = []
    sc_fdma_papr = []

    for _ in range(trials):
        data = (np.random.choice([-1, 1], size=data_subcarriers) + 1j * np.random.choice([-1, 1], size=data_subcarriers)) / np.sqrt(2)

        freq_domain = np.zeros(n_subcarriers, dtype=complex)
        freq_domain[:data_subcarriers] = data
        ofdm_time = np.fft.ifft(freq_domain)
        ofdm_papr.append(10 * np.log10(calculate_papr(ofdm_time)))

        dft_spread = np.fft.fft(data)
        sc_freq = np.zeros(n_subcarriers, dtype=complex)
        sc_freq[:data_subcarriers] = dft_spread
        sc_time = np.fft.ifft(sc_freq)
        sc_fdma_papr.append(10 * np.log10(calculate_papr(sc_time)))

    return np.array(ofdm_papr), np.array(sc_fdma_papr)


def main() -> None:
    np.random.seed(3)
    ofdm, sc_fdma = simulate()

    labels = ["OFDM", "SC-FDMA"]
    means = [ofdm.mean(), sc_fdma.mean()]
    stds = [ofdm.std(), sc_fdma.std()]

    plt.figure(figsize=(6, 4))
    bars = plt.bar(labels, means, yerr=stds, color=["#1f77b4", "#ff7f0e"], capsize=6)
    for bar, mean in zip(bars, means):
        plt.text(bar.get_x() + bar.get_width() / 2, mean + 0.3, f"{mean:.1f} dB", ha="center", va="bottom")

    plt.title("PAPR Comparison: OFDM vs SC-FDMA")
    plt.ylabel("Peak-to-Average Power Ratio (dB)")
    plt.grid(axis="y", alpha=0.3, linestyle=":")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
