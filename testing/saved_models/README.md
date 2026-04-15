# saved_models/

Place trained model checkpoints here before running tests.

| File | Module | Description |
|---|---|---|
| `segformer_flood.pth` | `satellite/segformer.py` | Modified SegFormer weights |
| `xception_flood.pth` | `satellite/flood_validation.py` | Xception flood classifier checkpoint |
| `vfnet_res2net101.pth` | `uav/varifocalnet.py` | VarifocalNet Res2Net-101-DCN weights |

Tests that require a missing checkpoint are automatically **skipped** with a `[SKIP]` message — they do not fail.
