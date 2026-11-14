"""Unit tests for preprocessing pipeline: cleaning, normalization, indices, and PCA."""

from __future__ import annotations

import numpy as np

from terraspectra.data.preprocess.clean import (
    clean_nan_and_inf,
    clip_reflectance,
    drop_bad_bands,
    generate_qa_report,
    remove_spectral_spikes,
    smooth_savgol,
)
from terraspectra.data.preprocess.indices import build_index_stack, compute_ndvi, compute_pri
from terraspectra.data.preprocess.normalize import (
    WelfordAccumulator,
    standard_normal_variate,
    standardize_cube,
)
from terraspectra.data.preprocess.pca import CubePCA
from terraspectra.data.preprocess.pipeline import PreprocessingPipeline
from terraspectra.synth.wavelengths import make_wavelengths


def test_cleaning_modules() -> None:
    """Test bad band dropping, NaN repair, spike removal, and SavGol smoothing."""
    wls = make_wavelengths(224)
    cube = np.random.rand(224, 32, 32).astype(np.float32)

    # Inject bad values
    cube[10, 5, 5] = np.nan
    cube[20, :, :] = -9999.0
    cube[50, 10, 10] = 50.0  # Spike

    cleaned, val_wls, mask = drop_bad_bands(cube, wls)
    assert len(val_wls) < 224

    repaired, n_bad = clean_nan_and_inf(cleaned)
    assert not np.any(np.isnan(repaired))
    assert not np.any(repaired == -9999.0)

    spikeless = remove_spectral_spikes(repaired)
    assert spikeless[50, 10, 10] < 5.0

    smoothed = smooth_savgol(spikeless)
    assert smoothed.shape == spikeless.shape


def test_normalization_and_welford() -> None:
    """Test Welford running stats accumulator and Z-score standardization."""
    cube = np.random.normal(loc=0.5, scale=0.15, size=(30, 20, 20)).astype(np.float32)
    acc = WelfordAccumulator(n_bands=30)
    acc.update(cube)
    stats = acc.finalize()

    assert stats.count == 400
    np.testing.assert_allclose(stats.mean, np.mean(cube, axis=(1, 2)), atol=1e-4)

    std_cube = standardize_cube(cube, stats)
    # Check standardized mean is approx 0 and std is approx 1
    np.testing.assert_allclose(np.mean(std_cube, axis=(1, 2)), 0.0, atol=1e-3)
    np.testing.assert_allclose(np.std(std_cube, axis=(1, 2)), 1.0, atol=1e-2)

    # Test SNV
    snv = standard_normal_variate(cube)
    assert snv.shape == cube.shape


def test_spectral_indices() -> None:
    """Test NDVI and PRI calculations."""
    wls = make_wavelengths(224)
    cube = np.zeros((224, 10, 10), dtype=np.float32)
    # NIR > Red -> positive NDVI
    idx_800 = int(np.argmin(np.abs(wls - 800.0)))
    idx_670 = int(np.argmin(np.abs(wls - 670.0)))
    cube[idx_800] = 0.60
    cube[idx_670] = 0.10

    ndvi = compute_ndvi(cube, wls)
    assert np.all(ndvi > 0.65)

    stack, names = build_index_stack(cube, wls)
    assert stack.shape == (6, 10, 10)
    assert len(names) == 6


def test_incremental_pca_and_pipeline() -> None:
    """Test IncrementalPCA projection and end-to-end PreprocessingPipeline."""
    wls = make_wavelengths(64)
    cube = np.random.rand(64, 30, 30).astype(np.float32)

    pca = CubePCA(n_components=8)
    pca.fit_array(cube)
    assert pca.is_fitted

    reduced = pca.transform_cube(cube)
    assert reduced.shape == (8, 30, 30)

    err = pca.reconstruction_error(cube)
    assert err >= 0.0

    # Pipeline
    pipeline = PreprocessingPipeline(pca_components=8)
    res = pipeline.process_cube(cube, wls, scene_id="pipe_test")
    assert res.pca_cube.shape == (8, 30, 30)
    assert "clean_bands" in res.qa_report

