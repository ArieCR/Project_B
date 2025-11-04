import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    n_subcarriers = 64
    cp_length = 16
    occupied = np.arange(-26, 27)
    occupied = occupied[occupied != 0]

    qpsk_symbols = (
        np.random.choice([-1, 1], size=occupied.size)
        + 1j * np.random.choice([-1, 1], size=occupied.size)
    ) / np.sqrt(2)

    freq_domain = np.zeros(n_subcarriers, dtype=complex)
    freq_domain[occupied % n_subcarriers] = qpsk_symbols

    time_domain = np.fft.ifft(np.fft.ifftshift(freq_domain))
    cyclic_prefix = time_domain[-cp_length:]
    ofdm_symbol = np.concatenate([cyclic_prefix, time_domain])

    time_axis = np.arange(ofdm_symbol.size)

    plt.figure(figsize=(8, 4))
    plt.plot(time_axis, ofdm_symbol.real, label="In-phase")
    plt.plot(time_axis, ofdm_symbol.imag, label="Quadrature", alpha=0.7)
    plt.axvspan(0, cp_length, color="#ff7f0e", alpha=0.2, label="Cyclic Prefix")
    plt.title("OFDM Symbol with Cyclic Prefix")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(alpha=0.3, linestyle=":")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    np.random.seed(42)
    main()
