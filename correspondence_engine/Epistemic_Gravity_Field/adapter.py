"""
EGF Adapter: Thermodynamic Observation Layer
Tokens stream freely; thoughts are observed here.
"""

import torch
import numpy as np
from typing import Dict, Any

from correspondence_engine.Epistemic_Gravity_Field.space_field import SpaceFieldCognition


class EGFAdapter:
    def __init__(self, device: str = "cpu"):
        self.device = device
        self.field = SpaceFieldCognition(device=device)
        # Warm up the field to establish the gravity gradient baseline
        for _ in range(50):
            self.field.step()

    def _text_to_signal(self, text: str) -> torch.Tensor:
        """
        Converts a semantic thought chunk into a 32x32x32x4 tensor signal 
        for additive diffusion injection. Uses deterministic text seeding 
        to simulate epistemic heat/shock without heavy transformer overhead.
        """
        # Create a stable pseudo-random tensor influenced by text length and hash
        seed = abs(hash(text)) % (2**32)
        torch.manual_seed(seed)
        
        # Scale magnitude based on text intensity/length
        magnitude = min(float(len(text)) / 100.0, 5.0)
        signal = torch.randn(32, 32, 32, 4, device=self.device) * 0.1 * magnitude
        return signal

    def observe_chunk(self, chunk_text: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Observes a completed thought chunk or candidate output.
        Injects thermodynamic signal, steps the voxel grid, and returns field pressure metrics.
        """
        context = context or {}
        
        # 1. Convert text chunk to diffusion field stimulus
        signal = self._text_to_signal(chunk_text)
        
        # 2. Broadcast and step the field
        self.field.broadcast_to_field(signal)
        self.field.step()
        
        # 3. Gather field diagnostics
        stats = self.field.get_field_stats()
        
        center_entropy = stats.get('center_entropy', 0.0)
        outer_entropy = stats.get('outer_entropy', 0.0)
        renewal_pressure = stats.get('renewal_pressure', 0.0)
        
        # Compute derived metadata
        gradient_gap = outer_entropy - center_entropy
        is_shocked = outer_entropy > (center_entropy * 2.0)

        return {
            "center_entropy": center_entropy,
            "outer_entropy": outer_entropy,
            "gradient_gap": gradient_gap,
            "renewal_pressure": renewal_pressure,
            "is_shocked": is_shocked,
            "advisory": "stable" if gradient_gap > 0 else "turbulence_detected"
        }