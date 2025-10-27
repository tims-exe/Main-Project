import pickle
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
import snntorch.spikegen as spikegen
from collections import Counter
from sklearn.model_selection import train_test_split


# =====================================
# Class Imbalance Analysis
# =====================================
def analyze_class_imbalance(y, dataset_name="Dataset"):
    """Analyze and print class imbalance statistics."""
    unique, counts = np.unique(y, return_counts=True)
    
    total = len(y)
    max_count = counts.max()
    min_count = counts.min()
    imbalance_ratio = max_count / min_count
    
    print(f"\n{'='*70}")
    print(f"📊 {dataset_name.upper()} - CLASS IMBALANCE ANALYSIS")
    print(f"{'='*70}")
    print(f"Total samples: {total}")
    print(f"Imbalance ratio (max/min): {imbalance_ratio:.2f}x\n")
    
    print(f"{'Class':<8} {'Count':<10} {'Percentage':<12} {'Weight':<10}")
    print("-" * 70)
    
    # Calculate inverse frequency weights
    weights = {cls: 1.0 / count for cls, count in zip(unique, counts)}
    
    for cls, count in zip(unique, counts):
        pct = 100 * count / total
        weight = weights[cls]
        bar_length = int(pct / 3)
        bar = "█" * bar_length
        print(f"{cls:<8} {count:<10} {pct:>6.2f}% {bar:<20} {weight:.4f}")
    
    print(f"{'='*70}\n")
    
    return imbalance_ratio


# =====================================
# Augmentation utilities
# =====================================
def temporal_jitter(spike_train, max_shift=2):
    """Apply temporal jitter to spike trains."""
    shift = np.random.randint(-max_shift, max_shift + 1)
    out = np.zeros_like(spike_train)
    if shift > 0:
        out[shift:] = spike_train[:-shift]
    elif shift < 0:
        out[:shift] = spike_train[-shift:]
    else:
        out = spike_train.copy()
    return np.clip(out, 0, 1)


def add_noise(spike_train, noise_level=0.05):
    """Add Gaussian noise to spike trains."""
    noise = np.random.randn(*spike_train.shape) * noise_level
    spike_train = spike_train + noise
    return np.clip(spike_train, 0, 1)


def random_mask(spike_train, mask_prob=0.1):
    """Apply random masking to temporal dimension."""
    mask = np.random.rand(spike_train.shape[0]) > mask_prob
    spike_train = spike_train * mask[:, None]
    return spike_train, mask


# =====================================
# Dataset class
# =====================================
class MELDAudioSpikesAugmented(Dataset):
    """Dataset for MELD audio emotion classification."""
    
    def __init__(self, X, y, T=8, augment=False, spike_cap=1.0):
        self.X = X
        self.y = y
        self.T = T
        self.augment = augment
        self.spike_cap = spike_cap

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        x = torch.tensor(self.X[idx], dtype=torch.float32)
        y = torch.tensor(self.y[idx], dtype=torch.long)

        S = spikegen.rate(x, num_steps=self.T).float()
        mask = np.ones(self.T, dtype=bool)

        if self.augment:
            S_np = S.numpy()
            S_np = temporal_jitter(S_np)
            S_np = add_noise(S_np)
            S_np, mask = random_mask(S_np)
            S = torch.tensor(S_np, dtype=torch.float32)
        
        S = torch.clamp(S, 0, self.spike_cap)
        return S, y, torch.tensor(mask, dtype=torch.bool)


# =====================================
# Custom collate function
# =====================================
def collate_fn_spike(batch):
    """Custom collate function for spike batches."""
    spikes, labels, masks = zip(*batch)
    spikes = torch.stack(spikes, dim=0)
    labels = torch.stack(labels, dim=0)
    masks = torch.stack(masks, dim=0)
    return spikes, labels, masks


# =====================================
# Main data loading function (RECOMMENDED APPROACH)
# =====================================
def create_balanced_splits(
    features_path,
    labels_path,
    batch_size=32,
    T=8,
    augment=True,
    val_split=0.1,
    test_split=0.1,
    num_workers=0,
    use_weighted_sampling=True,
):
    """
    Create balanced train/val/test splits using WEIGHTED SAMPLING.
    
    Args:
        features_path: Path to pickled features
        labels_path: Path to pickled labels
        batch_size: Batch size for data loaders
        T: Number of timesteps for spike generation
        augment: Apply augmentations to training set
        val_split: Validation split ratio
        test_split: Test split ratio
        num_workers: Number of worker processes
        use_weighted_sampling: Use weighted sampling for class balance (RECOMMENDED)
    
    Returns:
        train_loader, val_loader, test_loader: DataLoader objects
    """
    
    # Load data
    print("📥 Loading data...")
    with open(features_path, "rb") as f:
        train_emb, val_emb, test_emb = pickle.load(f)
    merged_features = {**train_emb, **val_emb, **test_emb}

    with open(labels_path, "rb") as f:
        data_list = pickle.load(f)
        utter_list = data_list[0]
        label_idx = data_list[5]

    # Process features and labels
    print("🔄 Processing features and labels...")
    feats, labels = [], []
    for u in utter_list:
        key = f"{u['dialog']}_{u['utterance']}"
        if key in merged_features:
            x = merged_features[key].astype(np.float32)
            x = x / (np.linalg.norm(x) + 1e-8)
            x = np.clip(x, 0, 1.0)
            feats.append(x)
            labels.append(label_idx[u["y"]])

    X = np.stack(feats)
    y = np.array(labels, dtype=np.int64)

    print(f"✅ Loaded: {len(X)} samples, {X.shape[1]} features")
    analyze_class_imbalance(y, "Full Dataset")

    # Stratified split
    print("📊 Creating stratified splits...")
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=(val_split + test_split), stratify=y, random_state=42
    )

    rel_test_size = test_split / (val_split + test_split)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=rel_test_size, stratify=y_temp, random_state=42
    )

    print(f"📁 Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}\n")

    # Analyze training set imbalance
    analyze_class_imbalance(y_train, "Training Set")

    # Create datasets
    print("🔧 Creating datasets...")
    train_set = MELDAudioSpikesAugmented(X_train, y_train, T=T, augment=augment)
    val_set = MELDAudioSpikesAugmented(X_val, y_val, T=T, augment=False)
    test_set = MELDAudioSpikesAugmented(X_test, y_test, T=T, augment=False)

    # Create samplers
    if use_weighted_sampling:
        print("⚖️  Using weighted sampling for class balance...\n")
        
        # Compute inverse frequency weights
        class_counts = Counter(y_train)
        max_count = max(class_counts.values())
        
        # Weight each sample by inverse class frequency
        weights = []
        for label in y_train:
            weight = max_count / class_counts[label]
            weights.append(weight)
        
        weights = np.array(weights)
        
        # Normalize weights
        weights = weights / weights.sum() * len(weights)
        
        sampler = WeightedRandomSampler(
            weights=weights.tolist(),
            num_samples=len(y_train),
            replacement=True
        )
        
        train_loader = DataLoader(
            train_set,
            batch_size=batch_size,
            sampler=sampler,  # Use sampler instead of shuffle
            collate_fn=collate_fn_spike,
            num_workers=num_workers,
            pin_memory=(num_workers > 0),
            drop_last=True
        )
    else:
        # Simple shuffle without weighting
        train_loader = DataLoader(
            train_set,
            batch_size=batch_size,
            shuffle=True,
            collate_fn=collate_fn_spike,
            num_workers=num_workers,
            pin_memory=(num_workers > 0),
            drop_last=True
        )
    
    # Val and test loaders
    val_loader = DataLoader(
        val_set,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn_spike,
        num_workers=num_workers,
        pin_memory=(num_workers > 0),
        drop_last=False
    )
    
    test_loader = DataLoader(
        test_set,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn_spike,
        num_workers=num_workers,
        pin_memory=(num_workers > 0),
        drop_last=False
    )

    print(f"✅ DataLoaders created:")
    print(f"   Train: {len(train_loader)} batches")
    print(f"   Val: {len(val_loader)} batches")
    print(f"   Test: {len(test_loader)} batches\n")

    return train_loader, val_loader, test_loader
