import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def save_displacement_map_sync(
    img1: np.ndarray,
    U: np.ndarray,
    V: np.ndarray,
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    output_dir: str,
    filename: str = None,
) -> str:
    """
    Синхронное сохранение карты смещений БЕЗ ВЕКТОРОВ.
    """
    if filename is None:
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"displacement_map_{timestamp}.png"

    filepath = os.path.join(output_dir, filename)

    fig, ax = plt.subplots(figsize=(12, 10))

    magnitude = np.sqrt(U**2 + V**2)

    ax.imshow(img1, cmap="gray", alpha=0.2, extent=[0, img1.shape[1], img1.shape[0], 0])

    im = ax.imshow(
        magnitude,
        cmap="hot_r",
        alpha=0.85,
        extent=[x_coords[0], x_coords[-1], y_coords[-1], y_coords[0]],
        vmin=0,
        vmax=np.nanmax(magnitude),
    )

    ax.set_title(
        "Карта смещений материала\n(красный - большие смещения, синий - малые)",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("X (пиксели)", fontsize=12)
    ax.set_ylabel("Y (пиксели)", fontsize=12)
    ax.grid(True, alpha=0.2, linestyle="--", linewidth=0.5)

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Магнитуда смещений (пиксели)", fontsize=11)

    stats_text = f"""
    Статистика смещений:
    Среднее: {np.nanmean(magnitude):.3f} пикселей
    Максимум: {np.nanmax(magnitude):.3f} пикселей
    Медиана: {np.nanmedian(magnitude):.3f} пикселей
    Стандартное отклонение: {np.nanstd(magnitude):.3f} пикселей
    """
    ax.text(
        0.02,
        0.98,
        stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9),
    )

    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return filepath


async def display_results(results: Dict[str, Any]):
    """
    Отображение результатов обработки.
    """
    if results["status"] == "completed":
        pass
    else:
        logger.error(
            "Тест %s завершился с ошибкой: %s", results["test_id"], results.get("error", "Неизвестная ошибка")
        )


def save_three_images_sync(
    img1: np.ndarray,
    img2: np.ndarray,
    U: np.ndarray,
    V: np.ndarray,
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    output_dir: str,
    test_id: str,
) -> Dict[str, str]:
    """
    Синхронное сохранение трех изображений.
    """
    magnitude = np.sqrt(U**2 + V**2)

    fig1, ax1 = plt.subplots(figsize=(8, 6))
    ax1.imshow(img1, cmap="gray")
    ax1.set_title("Исходное изображение (до испытания)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("X (пиксели)", fontsize=10)
    ax1.set_ylabel("Y (пиксели)", fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
    img1_path = os.path.join(output_dir, f"{test_id}_original.png")
    plt.tight_layout()
    plt.savefig(img1_path, dpi=200, bbox_inches="tight")
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.imshow(img2, cmap="gray")
    ax2.set_title("Изображение после испытания", fontsize=12, fontweight="bold")
    ax2.set_xlabel("X (пиксели)", fontsize=10)
    ax2.set_ylabel("Y (пиксели)", fontsize=10)
    ax2.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
    img2_path = os.path.join(output_dir, f"{test_id}_deformed.png")
    plt.tight_layout()
    plt.savefig(img2_path, dpi=200, bbox_inches="tight")
    plt.close(fig2)

    fig3, ax3 = plt.subplots(figsize=(10, 8))

    im = ax3.imshow(
        magnitude,
        cmap="hot_r",
        extent=[x_coords[0], x_coords[-1], y_coords[-1], y_coords[0]],
        vmin=0,
        vmax=np.nanmax(magnitude),
    )

    ax3.set_title(
        "Карта смещений\n(красный - большие смещения, белый - малые)",
        fontsize=12,
        fontweight="bold",
    )
    ax3.set_xlabel("X (пиксели)", fontsize=10)
    ax3.set_ylabel("Y (пиксели)", fontsize=10)
    ax3.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)

    cbar = plt.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)
    cbar.set_label("Магнитуда смещений (пиксели)", fontsize=10)

    stats_text = f"""
    Статистика смещений:
    Среднее: {np.nanmean(magnitude):.3f} px
    Максимум: {np.nanmax(magnitude):.3f} px
    Медиана: {np.nanmedian(magnitude):.3f} px
    """
    ax3.text(
        0.02,
        0.98,
        stats_text,
        transform=ax3.transAxes,
        fontsize=9,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    img3_path = os.path.join(output_dir, f"{test_id}_displacement.png")
    plt.tight_layout()
    plt.savefig(img3_path, dpi=200, bbox_inches="tight")
    plt.close(fig3)

    return {
        "original_image": img1_path,
        "deformed_image": img2_path,
        "displacement_map": img3_path,
    }
    