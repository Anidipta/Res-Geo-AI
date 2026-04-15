"""UAV module: night vision, VarifocalNet detection, flight planning, and pipeline."""
from uav.night_vision import transform_to_night_vision, preprocess_for_detection
from uav.varifocalnet import VarifocalNet, load_vfnet
from uav.victim_detector import detect_victims_in_frame, detect_victims_batch
from uav.flight_planner import plan_uav_mission, generate_spiral_path
from uav.pipeline import run_uav_pipeline
