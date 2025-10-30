import torch
import torch.nn as nn
from spikingjelly.activation_based import layer, neuron, functional


class SpikeNetEfficient(nn.Module):
    """
    GPU-Efficient SpikeNet with same input/output signature.
    Input: (B, seq_len, 1611)
    Output: (B, 7)
    """
    
    def __init__(self, in_dim=1611, embed_dim=256, num_classes=7, T=32, dropout=0.1):
        super().__init__()
        self.T = T
        
        # Dimensionality Reduction
        self.input_proj = layer.Linear(in_dim, embed_dim, bias=False)
        
        # Spiking Layers
        self.lif1 = neuron.LIFNode(tau=2.0, detach_reset=True, step_mode='m', v_threshold=1.0, v_reset=0.0)
        
        self.fc1 = layer.Linear(embed_dim, embed_dim, bias=False)
        self.lif2 = neuron.LIFNode(tau=2.0, detach_reset=True, step_mode='m', v_threshold=1.0, v_reset=0.0)
        
        self.fc2 = layer.Linear(embed_dim, embed_dim, bias=False)
        self.lif3 = neuron.LIFNode(tau=2.0, detach_reset=True, step_mode='m', v_threshold=1.0, v_reset=0.0)
        
        # Readout
        self.dropout = layer.Dropout(dropout)
        self.classifier = layer.Linear(embed_dim, num_classes, bias=True)
    
    def forward(self, x, mask=None):
        """
        Args:
            x: shape (B, seq_len, in_dim=1611)
            mask: optional (B, seq_len)
        
        Returns:
            logits: shape (B, num_classes=7)
        """
        B, L, D = x.shape
        x = x.to(torch.float32)
        functional.reset_net(self)
        
        # Dimensionality reduction
        x = self.input_proj(x)  # (B, L, 256)
        
        # Spike generation
        x = x.unsqueeze(0).repeat(self.T, 1, 1, 1)  # (T, B, L, 256)
        spikes = (torch.rand_like(x, device=x.device) <= torch.sigmoid(x)).float()
        
        # Spike processing
        x = self.lif1(spikes)  # (T, B, L, 256)
        x = self.fc1(x)  # (T, B, L, 256)
        x = self.lif2(x)  # (T, B, L, 256)
        x = self.fc2(x)  # (T, B, L, 256)
        x = self.lif3(x)  # (T, B, L, 256)
        
        # Aggregation
        x = x.mean(dim=2)  # (T, B, 256)
        x = x.mean(dim=0)  # (B, 256)
        
        # Classification
        x = self.dropout(x)  # (B, 256)
        logits = self.classifier(x)  # (B, 7)
        
        return logits


class SpikeNet(SpikeNetEfficient):
    """Backward compatible alias."""
    
    def __init__(self, in_dim, embed_dim, num_classes, T=32, dropout=0.1):
        super().__init__(in_dim=in_dim, embed_dim=embed_dim, num_classes=num_classes, T=T, dropout=dropout)
