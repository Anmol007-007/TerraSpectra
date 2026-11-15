"""Unit tests for patch extraction, dataset, augmentation, splits, and dataloader."""

from __future__ import annotations

import unittest
import numpy as np

try:
    import torch
except ImportError:
    torch = None  # type: ignore[assignment]

from terraspectra.data.augment import (
    BandDropout,
    Compose,
    GaussianNoise,
    RandomSpatialFlip,
    SpectralJitter,
)
from terraspectra.data.dataset import HyperspectralPatchDataset
from terraspectra.data.loaders import build_dataloader
from terraspectra.data.patches import (
    PatchSpec,
    build_patch_index,
    extract_patch_with_padding,
)
from terraspectra.data.splits import spatial_block_split


class TestDatasetLoaders(unittest.TestCase):
    def test_patch_extraction_interior_and_border(self) -> None:
        """Test 3D patch extraction with reflection padding at image boundaries."""
        cube = np.random.rand(32, 50, 50).astype(np.float32)

        # Interior patch
        p_int = extract_patch_with_padding(cube, center_r=25, center_c=25, patch_size=11)
        self.assertEqual(p_int.shape, (32, 11, 11))
        np.testing.assert_allclose(p_int, cube[:, 20:31, 20:31])

        # Corner patch (center at (0, 0)) - requires reflection padding
        p_corner = extract_patch_with_padding(cube, center_r=0, center_c=0, patch_size=11)
        self.assertEqual(p_corner.shape, (32, 11, 11))
        # Center pixel of extracted patch (idx 5, 5) matches original (0, 0)
        np.testing.assert_allclose(p_corner[:, 5, 5], cube[:, 0, 0])

    def test_build_patch_index_and_dataset(self) -> None:
        """Test patch index generation and PyTorch Dataset iteration."""
        h, w = 60, 60
        state_mask = np.zeros((h, w), dtype=np.uint8)
        state_mask[20:30, 20:30] = 1  # Pre-symptomatic stress
        state_mask[30:35, 30:35] = 2  # Visible disease

        sev_mask = np.full((h, w), 0.1, dtype=np.float32)
        sev_mask[state_mask == 1] = 0.45
        sev_mask[state_mask == 2] = 0.85

        days_to_sym = np.full((h, w), np.nan, dtype=np.float32)
        days_to_sym[state_mask == 1] = 14.0
        days_to_sym[state_mask == 2] = 0.0

        farm_mask = np.ones((h, w), dtype=bool)

        specs = build_patch_index(
            state_mask=state_mask,
            severity_mask=sev_mask,
            days_to_symptoms=days_to_sym,
            farm_mask=farm_mask,
            patch_size=11,
            stride=2,
            balanced_sampling=True,
            samples_per_class=20,
        )
        self.assertGreater(len(specs), 0)

        # Dataset test
        cube = np.random.rand(32, h, w).astype(np.float32)
        ds = HyperspectralPatchDataset(cube_or_reader=cube, patch_specs=specs)
        self.assertEqual(len(ds), len(specs))

        item = ds[0]
        # Check tensor shape [1, D, H, W]
        self.assertEqual(item["patch"].shape, (1, 32, 11, 11))
        self.assertIsNotNone(item["state"])
        self.assertIsNotNone(item["severity"])

    def test_spatial_block_splits_no_leakage(self) -> None:
        """Assert spatial block splitter has zero index overlap between train, val, and test."""
        specs = [
            PatchSpec(
                center_r=r,
                center_c=c,
                patch_size=11,
                state_label=0,
                severity=0.0,
                days_to_symptoms=-1.0,
            )
            for r in range(10, 110, 6)
            for c in range(10, 110, 6)
        ]

        train_idx, val_idx, test_idx = spatial_block_split(
            specs, grid_rows=128, grid_cols=128, block_size=32, buffer_pixels=2
        )

        s_train, s_val, s_test = set(train_idx), set(val_idx), set(test_idx)
        self.assertEqual(len(s_train.intersection(s_val)), 0)
        self.assertEqual(len(s_train.intersection(s_test)), 0)
        self.assertEqual(len(s_val.intersection(s_test)), 0)

    def test_augmentation_compose(self) -> None:
        """Test spectral and spatial augmentation pipeline."""
        patch = np.ones((32, 11, 11), dtype=np.float32)
        aug = Compose([
            SpectralJitter((0.98, 1.02)),
            GaussianNoise(0.005),
            BandDropout(0.05),
            RandomSpatialFlip(),
        ])
        augmented = aug(patch)
        self.assertEqual(augmented.shape, patch.shape)

    def test_dataloader_batch_shapes(self) -> None:
        """Test PyTorch DataLoader batch tensor shapes [B_batch, 1, D, H, W]."""
        cube = np.random.rand(16, 50, 50).astype(np.float32)
        specs = [
            PatchSpec(
                center_r=25,
                center_c=25,
                patch_size=11,
                state_label=1,
                severity=0.5,
                days_to_symptoms=14.0,
            )
            for _ in range(8)
        ]
        ds = HyperspectralPatchDataset(cube_or_reader=cube, patch_specs=specs)
        loader = build_dataloader(ds, batch_size=4, shuffle=False)

        batch = next(iter(loader))
        self.assertEqual(batch["patches"].shape, (4, 1, 16, 11, 11))
        self.assertEqual(batch["states"].shape, (4,))
        self.assertEqual(batch["severities"].shape, (4,))


if __name__ == "__main__":
    unittest.main()
