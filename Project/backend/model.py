import torch
import torch.nn as nn

class SpikeAttentionNet(nn.Module):
    def __init__(self, in_dim, embed_dim, num_heads, num_classes, dropout=0.1):
        super().__init__()
        self.embed = nn.Linear(in_dim, embed_dim)
        self.layernorm = nn.LayerNorm(embed_dim)  # add this
        self.attn = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout, batch_first=True)
        self.fc = nn.Sequential(
            nn.LayerNorm(embed_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim, num_classes)
        )

    def forward(self, x, mask=None):
        x = self.embed(x)
        x = self.layernorm(x)                         # normalize before attention
        x = torch.clamp(x, -5, 5)                     # clamp to prevent overflow
        attn_out, _ = self.attn(x, x, x, key_padding_mask=~mask if mask is not None else None)
        attn_out = torch.nan_to_num(attn_out)         # clean up any accidental NaNs
        pooled = attn_out.mean(dim=1)
        logits = self.fc(pooled)
        logits = torch.nan_to_num(logits)
        return logits
