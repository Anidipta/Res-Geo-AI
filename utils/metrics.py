"""Evaluation metrics: IoU, mIoU, precision, recall, F1, MPR for model benchmarking."""

import numpy as np
from typing import List, Dict, Tuple, Optional


def compute_iou(pred_mask: np.ndarray, true_mask: np.ndarray, class_id: int) -> float:
    # Compute per-class IoU from predicted and ground truth segmentation masks
    pred_c = (pred_mask == class_id)
    true_c = (true_mask == class_id)
    tp = int((pred_c & true_c).sum())
    fp = int((pred_c & ~true_c).sum())
    fn = int((~pred_c & true_c).sum())
    denom = tp + fp + fn
    return float(tp / denom) if denom > 0 else 0.0


def compute_miou(pred_mask: np.ndarray, true_mask: np.ndarray, num_classes: int) -> float:
    # Average IoU across all classes for semantic segmentation evaluation
    ious = [compute_iou(pred_mask, true_mask, c) for c in range(num_classes)]
    return float(np.mean(ious))


def compute_precision(tp: int, fp: int) -> float:
    # Standard precision: TP / (TP + FP)
    return float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0


def compute_recall(tp: int, fn: int) -> float:
    # Standard recall: TP / (TP + FN)
    return float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0


def compute_f1(precision: float, recall: float) -> float:
    # Harmonic mean of precision and recall
    denom = precision + recall
    return float(2 * precision * recall / denom) if denom > 0 else 0.0


def compute_mpr(tp_person: int, fn_person: int) -> float:
    # Miss Person Rate: 1 - Recall for the Person class (lower is better)
    recall = compute_recall(tp_person, fn_person)
    return float(1.0 - recall)


def compute_detection_metrics(detections: List[Dict], ground_truth: List[Dict],
                               iou_threshold: float = 0.5) -> Dict:
    # Match detections to GT boxes by IoU and compute P/R/F1 for all classes
    tp, fp, fn = 0, 0, 0
    tp_person, fn_person = 0, 0
    matched_gt = set()

    for det in detections:
        best_iou, best_gt_idx = 0.0, -1
        for gi, gt in enumerate(ground_truth):
            if gi in matched_gt:
                continue
            iou = _box_iou(det["bbox"], gt["bbox"])
            if iou > best_iou:
                best_iou, best_gt_idx = iou, gi
        if best_iou >= iou_threshold and best_gt_idx >= 0:
            tp += 1
            matched_gt.add(best_gt_idx)
            if det.get("class_name") == "Person":
                tp_person += 1
        else:
            fp += 1

    fn = len(ground_truth) - len(matched_gt)
    fn_person = sum(1 for gt in ground_truth if gt.get("class_name") == "Person") - tp_person

    prec = compute_precision(tp, fp)
    rec = compute_recall(tp, fn)
    f1 = compute_f1(prec, rec)
    mpr = compute_mpr(tp_person, fn_person)

    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": prec, "recall": rec, "f1": f1,
        "tp_person": tp_person, "fn_person": fn_person, "mpr": mpr
    }


def _box_iou(box_a: List[float], box_b: List[float]) -> float:
    # Compute IoU between two [x1,y1,x2,y2] bounding boxes
    xa = max(box_a[0], box_b[0])
    ya = max(box_a[1], box_b[1])
    xb = min(box_a[2], box_b[2])
    yb = min(box_a[3], box_b[3])
    inter = max(0, xb - xa) * max(0, yb - ya)
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union = area_a + area_b - inter
    return float(inter / union) if union > 0 else 0.0


def compute_gps_localization_error(predicted: List[Dict], ground_truth: List[Dict]) -> Dict:
    # Compute mean, median, and max GPS localization error in meters
    if not predicted or not ground_truth:
        return {"mean_error": 0.0, "median_error": 0.0, "max_error": 0.0}
    errors = []
    for pred, gt in zip(predicted, ground_truth):
        dx = pred.get("gps_x", 0.0) - gt.get("gps_x", 0.0)
        dy = pred.get("gps_y", 0.0) - gt.get("gps_y", 0.0)
        errors.append(np.sqrt(dx ** 2 + dy ** 2))
    return {
        "mean_error": float(np.mean(errors)),
        "median_error": float(np.median(errors)),
        "max_error": float(np.max(errors)),
    }
