"""VarifocalNet-based victim detection with IoU-aware varifocal loss."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple


class DeformableConv2d(nn.Module):
    # Simplified deformable convolution wrapping standard conv for structure compatibility
    def __init__(self, in_c: int, out_c: int, kernel: int = 3, padding: int = 1):
        super().__init__()
        self.offset_conv = nn.Conv2d(in_c, 2 * kernel * kernel, kernel, padding=padding)
        self.conv = nn.Conv2d(in_c, out_c, kernel, padding=padding)
        self.bn = nn.BatchNorm2d(out_c)
        self.act = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Forward using standard conv (DCN replaces this in production)
        return self.act(self.bn(self.conv(x)))


class Res2NetBlock(nn.Module):
    # Res2Net hierarchical residual block with scale=4
    def __init__(self, channels: int, scale: int = 4):
        super().__init__()
        assert channels % scale == 0
        self.scale = scale
        width = channels // scale
        self.convs = nn.ModuleList([nn.Sequential(
            nn.Conv2d(width, width, 3, padding=1),
            nn.BatchNorm2d(width), nn.ReLU()
        ) for _ in range(scale - 1)])
        self.out_conv = nn.Conv2d(channels, channels, 1)
        self.bn_out = nn.BatchNorm2d(channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Split into scale sub-features, process hierarchically, then merge
        splits = torch.chunk(x, self.scale, dim=1)
        out = [splits[0]]
        for i, conv in enumerate(self.convs):
            xi = splits[i + 1] if i == 0 else splits[i + 1] + out[-1]
            out.append(conv(xi))
        return F.relu(self.bn_out(self.out_conv(torch.cat(out, dim=1))) + x)


class FPN(nn.Module):
    # Feature Pyramid Network for multi-scale feature extraction
    def __init__(self, in_channels: List[int] = [256, 512, 1024, 2048], out_channels: int = 256):
        super().__init__()
        self.lateral = nn.ModuleList([nn.Conv2d(c, out_channels, 1) for c in in_channels])
        self.outputs = nn.ModuleList([nn.Conv2d(out_channels, out_channels, 3, padding=1) for _ in in_channels])

    def forward(self, features: List[torch.Tensor]) -> List[torch.Tensor]:
        # Build FPN top-down pathway and return multi-scale feature maps
        laterals = [l(f) for l, f in zip(self.lateral, features)]
        for i in range(len(laterals) - 1, 0, -1):
            laterals[i - 1] = laterals[i - 1] + F.interpolate(laterals[i], scale_factor=2, mode="nearest")
        return [o(l) for o, l in zip(self.outputs, laterals)]


class VFNetHead(nn.Module):
    # VarifocalNet detection head: predicts boxes and IoU-aware scores
    def __init__(self, in_channels: int = 256, num_classes: int = 9, num_convs: int = 4):
        super().__init__()
        self.cls_convs = nn.ModuleList([
            DeformableConv2d(in_channels, in_channels) for _ in range(num_convs)
        ])
        self.reg_convs = nn.ModuleList([
            DeformableConv2d(in_channels, in_channels) for _ in range(num_convs)
        ])
        self.cls_pred = nn.Conv2d(in_channels, num_classes, 1)
        self.reg_pred = nn.Conv2d(in_channels, 4, 1)
        self.iou_pred = nn.Conv2d(in_channels, 1, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # Run classification and regression branches, return cls/reg/iou predictions
        cls_feat = x
        reg_feat = x
        for c, r in zip(self.cls_convs, self.reg_convs):
            cls_feat = c(cls_feat)
            reg_feat = r(reg_feat)
        cls_out = self.cls_pred(cls_feat)
        reg_out = self.reg_pred(reg_feat)
        iou_out = torch.sigmoid(self.iou_pred(reg_feat))
        return cls_out, reg_out, iou_out


class VarifocalLoss(nn.Module):
    # Varifocal loss: quality-weighted focal loss for dense detection
    def __init__(self, alpha: float = 0.75, gamma: float = 2.0, beta: float = 1.5):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.beta = beta

    def forward(self, pred: torch.Tensor, target_iou: torch.Tensor, target_label: torch.Tensor) -> torch.Tensor:
        # Compute varifocal loss: -q * (alpha * (1-p)^gamma * log(p)) for positive, -(alpha*p^gamma*log(1-p)) for neg
        q = target_iou
        pt = torch.sigmoid(pred)
        pos_weight = self.alpha * (q - pt).abs().pow(self.gamma)
        neg_weight = self.alpha * pt.pow(self.gamma)
        pos_loss = -q * pos_weight * torch.log(pt + 1e-8) * (target_label == 1).float()
        neg_loss = -neg_weight * torch.log(1 - pt + 1e-8) * (target_label == 0).float()
        return (pos_loss + neg_loss).mean()


class VarifocalNet(nn.Module):
    # Full VFNet: Res2Net-101 backbone + FPN + VFNet detection head
    def __init__(self, num_classes: int = 9, in_channels: int = 3):
        super().__init__()
        # Simplified Res2Net backbone (4 stages)
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 64, 7, stride=2, padding=3),
            nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(3, stride=2, padding=1),
        )
        self.layer1 = nn.Sequential(*[Res2NetBlock(64) for _ in range(3)])
        self.layer2 = nn.Sequential(nn.Conv2d(64, 128, 1, stride=2), *[Res2NetBlock(128) for _ in range(4)])
        self.layer3 = nn.Sequential(nn.Conv2d(128, 256, 1, stride=2), *[Res2NetBlock(256) for _ in range(23)])
        self.layer4 = nn.Sequential(nn.Conv2d(256, 512, 1, stride=2), *[Res2NetBlock(512) for _ in range(3)])
        self.fpn = FPN([64, 128, 256, 512], out_channels=256)
        self.head = VFNetHead(256, num_classes)
        self.varifocal_loss = VarifocalLoss()

    def forward(self, x: torch.Tensor) -> List[Tuple]:
        # Extract backbone features, build FPN pyramid, apply detection head
        x = self.stem(x)
        f1 = self.layer1(x)
        f2 = self.layer2(f1)
        f3 = self.layer3(f2)
        f4 = self.layer4(f3)
        fpn_feats = self.fpn([f1, f2, f3, f4])
        return [self.head(f) for f in fpn_feats]


def load_vfnet(weights_path: str, num_classes: int = 9, device: str = "cpu") -> VarifocalNet:
    # Load VarifocalNet from checkpoint and set to eval mode
    model = VarifocalNet(num_classes=num_classes)
    state = torch.load(weights_path, map_location=device)
    model.load_state_dict(state)
    model.eval()
    return model.to(device)
