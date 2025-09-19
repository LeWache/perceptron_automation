import numpy as np
from numpy import polyfit


def estimate_background_gradient(x, y, min_segment_size=10, gap_width=5, slope_tolerance=0.0002):

    x = np.asarray(x)
    y = np.asarray(y)
    N = len(x)

    best_slope = None
    best_error = np.inf

    for split in range(min_segment_size + gap_width, N - min_segment_size - gap_width):
        # Define left and right segments, skipping the gap
        x1, y1 = x[:split - gap_width], y[:split - gap_width]
        x2, y2 = x[split + gap_width:], y[split + gap_width:]

        if len(x1) < min_segment_size or len(x2) < min_segment_size:
            continue

        # Linear fits
        m1, _ = np.polyfit(x1, y1, 1)
        m2, _ = np.polyfit(x2, y2, 1)

        # Check slope consistency
        if abs(m1 - m2) < slope_tolerance:
            y1_fit = m1 * x1 + np.mean(y1 - m1 * x1)
            y2_fit = m2 * x2 + np.mean(y2 - m2 * x2)
            total_error = np.sum((y1 - y1_fit)**2) + np.sum((y2 - y2_fit)**2)

            if total_error < best_error:
                best_error = total_error
                best_slope = (m1 + m2) / 2

    # Fallback
    if best_slope is None:
        best_slope, _ = np.polyfit(x, y, 1)

    return best_slope
