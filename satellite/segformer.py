"""Modified SegFormer architecture for flood semantic segmentation."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple


class SpectralNorm(nn.Module):
    # Wrapper applying spectral normalization to improve generalization
    def __init__(self, module: nn.Module):
        super().__init__()
        self.module = nn.utils.spectral_norm(module)

    def forward(self, x):
        return self.module(x)


class MultiscaleAttention(nn.Module):
    # Multi-scale attention for fine-grained spatial feature aggregation
    def __init__(self, dim: int, num_heads: int = 8, sr_ratios: List[int] = None):
        super().__init__()
        sr_ratios = sr_ratios or [8, 4, 2, 1]
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.scale = self.head_dim ** -0.5
        self.q = SpectralNorm(nn.Linear(dim, dim))
        self.kv_layers = nn.ModuleList([
            nn.Sequential(
                nn.Conv2d(dim, dim, sr, stride=sr),
                nn.LayerNorm(dim),
            ) for sr in sr_ratios
        ])
        self.proj = nn.Linear(dim, dim)

    def forward(self, x: torch.Tensor, H: int, W: int) -> torch.Tensor:
        # Apply multi-scale spatial reduction attention on feature map
        B, N, C = x.shape
        q = self.q(x).reshape(B, N, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        x_2d = x.permute(0, 2, 1).reshape(B, C, H, W)
        kv_list = []
        for kv_layer in self.kv_layers:
            kv_feat = kv_layer[0](x_2d)
            kv_feat = kv_feat.flatten(2).transpose(1, 2)
            kv_feat = kv_layer[1](kv_feat)
            kv_list.append(kv_feat)
        kv_concat = torch.cat(kv_list, dim=1)
        k = kv_concat.reshape(B, -1, self.num_heads, self.head_dim).permute(0, 2, 1, 3)
        v = k
        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        out = (attn @ v).transpose(1, 2).reshape(B, N, C)
        return self.proj(out)


class TransformerBlock(nn.Module):
    # Single transformer encoder block with multiscale attention and FFN
    def __init__(self, dim: int, num_heads: int, mlp_ratio: float = 4.0, sr_ratios: List[int] = None):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = MultiscaleAttention(dim, num_heads, sr_ratios)
        self.norm2 = nn.LayerNorm(dim)
        mlp_hidden = int(dim * mlp_ratio)
        self.mlp = nn.Sequential(
            nn.Linear(dim, mlp_hidden),
            nn.GELU(),
            nn.Linear(mlp_hidden, dim),
        )

    def forward(self, x: torch.Tensor, H: int, W: int) -> torch.Tensor:
        # Forward pass through attention and MLP sub-layers
        x = x + self.attn(self.norm1(x), H, W)
        x = x + self.mlp(self.norm2(x))
        return x


class HierarchicalEncoder(nn.Module):
    # 4-stage hierarchical transformer encoder (F0 → F4)
    STAGE_CONFIGS = [
        {"patch": 7, "stride": 4, "dim": 64,  "depth": 2, "heads": 1},
        {"patch": 3, "stride": 2, "dim": 128, "depth": 2, "heads": 2},
        {"patch": 3, "stride": 2, "dim": 320, "depth": 4, "heads": 5},
        {"patch": 3, "stride": 2, "dim": 512, "depth": 2, "heads": 8},
    ]

    def __init__(self, in_channels: int = 3):
        super().__init__()
        self.stages = nn.ModuleList()
        self.patch_embeds = nn.ModuleList()
        self.norms = nn.ModuleList()
        c = in_channels
        for cfg in self.STAGE_CONFIGS:
            self.patch_embeds.append(
                nn.Conv2d(c, cfg["dim"], cfg["patch"], stride=cfg["stride"],
                          padding=cfg["patch"] // 2)
            )
            self.norms.append(nn.LayerNorm(cfg["dim"]))
            self.stages.append(nn.ModuleList([
                TransformerBlock(cfg["dim"], cfg["heads"]) for _ in range(cfg["depth"])
            ]))
            c = cfg["dim"]

    def forward(self, x: torch.Tensor) -> List[torch.Tensor]:
        # Extract multi-scale features F1..F4 from input satellite tile
        features = []
        for embed, norm, stage in zip(self.patch_embeds, self.norms, self.stages):
            x = embed(x)
            B, C, H, W = x.shape
            x = x.flatten(2).transpose(1, 2)
            x = norm(x)
            for blk in stage:
                x = blk(x, H, W)
            x = x.transpose(1, 2).reshape(B, C, H, W)
            features.append(x)
        return features


class SegFormerDecoder(nn.Module):
    # MLP-based all-MLP decode head for SegFormer
    def __init__(self, in_dims: List[int], embed_dim: int = 256, num_classes: int = 7):
        super().__init__()
        self.linear_layers = nn.ModuleList([
            nn.Linear(d, embed_dim) for d in in_dims
        ])
        self.fuse = nn.Sequential(
            nn.Conv2d(embed_dim * len(in_dims), embed_dim, 1),
            nn.BatchNorm2d(embed_dim),
            nn.ReLU(),
        )
        self.classify = nn.Conv2d(embed_dim, num_classes, 1)

    def forward(self, features: List[torch.Tensor], target_size: Tuple[int, int]) -> torch.Tensor:
        # Upsample and fuse multi-scale features then predict class logits
        H, W = target_size
        outs = []
        for feat, lin in zip(features, self.linear_layers):
            B, C, fh, fw = feat.shape
            feat = feat.flatten(2).transpose(1, 2)
            feat = lin(feat)
            feat = feat.transpose(1, 2).reshape(B, -1, fh, fw)
            feat = F.interpolate(feat, size=(H, W), mode="bilinear", align_corners=False)
            outs.append(feat)
        x = self.fuse(torch.cat(outs, dim=1))
        return self.classify(x)


class ModifiedSegFormer(nn.Module):
    # Full SegFormer model with multiscale attention encoder and MLP decoder
    def __init__(self, num_classes: int = 7, in_channels: int = 3):
        super().__init__()
        self.encoder = HierarchicalEncoder(in_channels)
        in_dims = [cfg["dim"] for cfg in HierarchicalEncoder.STAGE_CONFIGS]
        self.decoder = SegFormerDecoder(in_dims, embed_dim=256, num_classes=num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Forward pass returning per-pixel class logits at input resolution
        _, _, H, W = x.shape
        features = self.encoder(x)
        logits = self.decoder(features, (H // 4, W // 4))
        return F.interpolate(logits, size=(H, W), mode="bilinear", align_corners=False)

    def predict_flood_probability(self, x: torch.Tensor) -> torch.Tensor:
        # Return softmax flood-class probability map for input tile
        logits = self.forward(x)
        probs = torch.softmax(logits, dim=1)
        water_class_idx = 3
        return probs[:, water_class_idx, :, :]


def load_segformer(weights_path: str, num_classes: int = 7, device: str = "cpu") -> ModifiedSegFormer:
    # Instantiate and load pretrained SegFormer weights from disk
    model = ModifiedSegFormer(num_classes=num_classes)
    state = torch.load(weights_path, map_location=device)
    model.load_state_dict(state)
    model.eval()
    return model.to(device)
