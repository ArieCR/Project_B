import matplotlib.pyplot as plt
import numpy as np


def generate_qam_constellation(m: int) -> np.ndarray:
    side = int(np.sqrt(m))
    axis = np.linspace(-(side - 1), side - 1, side)
    xv, yv = np.meshgrid(axis, axis)
    constellation = xv.flatten() + 1j * yv.flatten()
    constellation /= np.sqrt((np.abs(constellation) ** 2).mean())
    return constellation


def generate_apsk_constellation(rings: tuple[int, int]) -> np.ndarray:
    outer_points = rings[0]
    inner_points = rings[1]

    outer = 1.2 * np.exp(1j * np.arange(outer_points) * (2 * np.pi / outer_points))
    inner = 0.6 * np.exp(
        1j
        * (np.arange(inner_points) * (2 * np.pi / inner_points) + np.pi / inner_points)
    )
    return np.concatenate([inner, outer])


def main() -> None:
    schemes = [
        ("16-QAM", generate_qam_constellation(16)),
        ("APSK (4+8)", generate_apsk_constellation((8, 4))),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for ax, (title, constellation) in zip(axes, schemes):
        ax.scatter(
            constellation.real,
            constellation.imag,
            c=np.abs(constellation),
            cmap="viridis",
            s=40,
        )
        ax.axhline(0, color="gray", linewidth=0.5)
        ax.axvline(0, color="gray", linewidth=0.5)
        ax.set_title(title)
        ax.set_xlabel("In-phase (I)")
        ax.set_ylabel("Quadrature (Q)")
        ax.set_aspect("equal", "box")
        ax.grid(alpha=0.3, linestyle=":")

    fig.suptitle("Symbol Mapping for Different Modulation Schemes")
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
