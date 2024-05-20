import numpy as np
from scipy import signal
from scipy import datasets
from scipy.ndimage import rotate
from visualization import plot_max_cross_correlation, plot_3d_topography
from image_utils import pad_or_crop_image


def scipy_example(normalize=True, add_noise=True):
    """
    Generates an example background image and filter from the scipy built-in dataset.

    Parameters:
    normalize (bool): If True, normalizes the images by subtracting the mean intensity.
    add_noise (bool): If True, adds Gaussian noise to the background image.

    Returns:
    tuple: A tuple containing:
        - background_image (numpy.ndarray): The generated background image.
        - filter (numpy.ndarray): The filter (a sub-region of the background image).
    """
    if normalize:
        # Load the grayscale face image and normalize it by subtracting the mean
        background_image = datasets.face(gray=True) - datasets.face(gray=True).mean()
        # Extract a sub-region of the face image (right eye) to use as the filter and normalize it by subtracting the mean
        filter = np.copy(background_image[300:365, 670:750])
        filter -= filter.mean()
    else:
        # Load the grayscale face image without normalization
        background_image = datasets.face(gray=True)
        # Extract a sub-region of the face image (right eye) to use as the filter
        filter = np.copy(background_image[300:365, 670:750])
    
    if add_noise:
        # Initialize random number generator
        rng = np.random.default_rng()
        # Add Gaussian noise to the background image
        background_image = background_image + rng.standard_normal(background_image.shape) * 50

    return background_image, filter


def cross_correlation(background_image, filter, return_max_loc=False):
    """
    Compute the cross-correlation between a background image and a filter image.

    Parameters:
    - background_image (numpy.ndarray): The background image.
    - filter (numpy.ndarray): The filter image.
    - return_max_loc (bool, optional): Whether to return the location of the maximum correlation. Default is False.

    Returns:
    - corr (numpy.ndarray): The cross-correlation result.
    - x (int): The x-coordinate of the maximum correlation (if return_max_loc=True).
    - y (int): The y-coordinate of the maximum correlation (if return_max_loc=True).
    """
    corr = signal.correlate2d(background_image, filter, boundary='symm', mode='same')
    if return_max_loc:
        y, x = np.unravel_index(np.argmax(corr), corr.shape)
        return corr, (x, y)
    return corr


def rotational_cc(background_image, filter, angle=10, return_average=False, return_max=False):
    """
    Compute the cross-correlation of a filter rotated by a certain angle over a background image.
    
    Args:
    background_image (numpy.ndarray): The larger image.
    filter (numpy.ndarray): The smaller image (filter).
    angle (int): The angle increment for rotating the filter.
    return_average (bool): Whether to return the average of the cross-correlation matrices.
    return_max (bool): Whether to return the maximum of the cross-correlation matrices.

    Returns:
    numpy.ndarray: The resulting cross-correlation matrices.
    list: The (x, y) locations of the maximum values for each rotation.
    """
    assert angle < 360
    filter_angle = 0
    all_correlations = []
    max_locs = []

    while filter_angle < 360:
        rotated_filter = rotate(filter, filter_angle, reshape=True)
        corr, max_loc = cross_correlation(background_image, rotated_filter, return_max_loc=True)
        all_correlations.append(corr)
        max_locs.append(max_loc)
        filter_angle += angle

    if return_average and return_max:
        return np.mean(all_correlations, axis=0), np.max(all_correlations, axis=0)
    elif return_average:
        return np.mean(all_correlations, axis=0)
    elif return_max:
        return np.max(all_correlations, axis=0)
    
    return all_correlations, max_locs


if __name__ == "__main__":
    # Example usage
    background_image = np.random.rand(100, 100)
    filter = np.random.rand(20, 20)

    corr, max_loc = cross_correlation(background_image, filter, return_max_loc=True)
    plot_max_cross_correlation(background_image, filter, corr, max_loc, save_path='2d_images.png')

    average_corr, max_corr = rotational_cc(background_image, filter, angle=10, return_average=True, return_max=True)

    # Save interactive plot to a file
    plot_3d_topography(average_corr, save_path='3d_avg_topography_plot.html')
    plot_3d_topography(max_corr, save_path='3d_max_topography_plot.html')