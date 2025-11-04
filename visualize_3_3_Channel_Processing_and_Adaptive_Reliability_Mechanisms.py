import numpy as np
import matplotlib.pyplot as plt


def amc_profile(snr_db: np.ndarray) -> np.ndarray:
    efficiency = np.zeros_like(snr_db, dtype=float)

    efficiency = np.where(snr_db >= 3, 0.67, efficiency)  # QPSK, rate 1/3
    efficiency = np.where(snr_db >= 6, 1.5, efficiency)  # QPSK, rate 3/4
    efficiency = np.where(snr_db >= 12, 3.0, efficiency)  # 16QAM, rate 3/4
    efficiency = np.where(snr_db >= 18, 4.5, efficiency)  # 64QAM, rate 3/4
    return efficiency


def harq_success_prob(snr_db: np.ndarray, max_retx: int = 2) -> tuple[np.ndarray, np.ndarray]:
    bler = np.clip(np.exp(-0.25 * (snr_db - 5)), 0, 1)
    baseline = 1 - bler
    combined = 1 - bler ** (max_retx + 1)
    return baseline, combined


def main() -> None:
    snr_db = np.linspace(0, 24, 200)
    spectral_eff = amc_profile(snr_db)
    no_harq, with_harq = harq_success_prob(snr_db)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)

    ax1.step(snr_db, spectral_eff, where="post", linewidth=2)
    ax1.set_ylabel("Spectral Efficiency (bits/s/Hz)")
    ax1.set_title("Adaptive Modulation and Coding (AMC)")
    ax1.grid(alpha=0.3, linestyle=":")
    ax1.text(4, 0.8, "QPSK 1/3", fontsize=9)
    ax1.text(8, 1.6, "QPSK 3/4", fontsize=9)
    ax1.text(14, 3.2, "16QAM 3/4", fontsize=9)
    ax1.text(20, 4.7, "64QAM 3/4", fontsize=9)

    ax2.plot(snr_db, no_harq, label="Single transmission", linewidth=2, color="#1f77b4")
    ax2.plot(snr_db, with_harq, label="HARQ (up to 3 tries)", linewidth=2, color="#ff7f0e")
    ax2.set_xlabel("SNR (dB)")
    ax2.set_ylabel("Packet Success Probability")
    ax2.set_title("Reliability Gain from HARQ")
    ax2.grid(alpha=0.3, linestyle=":")
    ax2.legend()

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
