import pickle
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
import snntorch.spikegen as spikegen
from collections import Counter
from sklearn.model_selection import train_test_split


# ------------------------------
# Augmentation utilities
# ------------------------------
def temporal_jitter(spike_train, max_shift=2):
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
    noise = np.random.randn(*spike_train.shape) * noise_level
    spike_train = spike_train + noise
    return np.clip(spike_train, 0, 1)

def random_mask(spike_train, mask_prob=0.1):
    mask = np.random.rand(spike_train.shape[0]) > mask_prob
    spike_train = spike_train * mask[:, None]
    return spike_train, mask


# ------------------------------
# Dataset class
# ------------------------------
class MELDAudioSpikesAugmented(Dataset):
    def __init__(
        self,
        X,
        y,
        T=25,
        augment=False,
        spike_cap=1.0,
    ):
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

        S = spikegen.rate(x, num_steps=self.T).float()  # [T, F]
        mask = np.ones(self.T, dtype=bool)

        if self.augment:
            S = S.numpy()
            S = temporal_jitter(S)
            S = add_noise(S)
            S, mask = random_mask(S)
            S = torch.tensor(S, dtype=torch.float32)

        return S, y, torch.tensor(mask, dtype=torch.bool)


# ------------------------------
# Load + Split + Oversample
# ------------------------------
def create_balanced_splits(
    features_path,
    labels_path,
    batch_size=64,
    T=25,
    augment=True,
    val_split=0.1,
    test_split=0.1,
):
    # ---- Load full data ----
    with open(features_path, "rb") as f:
        train_emb, val_emb, test_emb = pickle.load(f)
    merged_features = {**train_emb, **val_emb, **test_emb}

    with open(labels_path, "rb") as f:
        data_list = pickle.load(f)
        utter_list = data_list[0]
        label_idx = data_list[5]

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

    print(f"✅ Loaded dataset: N={len(X)}, F={X.shape[1]}")
    print("📊 Full class distribution:", Counter(y))

    # ---- Split into train, val, test ----
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=(val_split + test_split), stratify=y, random_state=42
    )

    rel_test_size = test_split / (val_split + test_split)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=rel_test_size, stratify=y_temp, random_state=42
    )

    print(f"📁 Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")

    # ---- Create datasets ----
    train_set = MELDAudioSpikesAugmented(X_train, y_train, T=T, augment=augment)
    val_set = MELDAudioSpikesAugmented(X_val, y_val, T=T, augment=False)
    test_set = MELDAudioSpikesAugmented(X_test, y_test, T=T, augment=False)

    # ---- Oversampling for train ----
    class_counts = Counter(y_train)
    weights = [1.0 / class_counts[c] for c in y_train]
    sampler = WeightedRandomSampler(weights, num_samples=len(y_train), replacement=True)

    print("🧠 Train class distribution:", Counter(y_train))
    print("🧪 Val class distribution:", Counter(y_val))
    print("🧩 Test class distribution:", Counter(y_test))
    print("📈 Oversampling applied to train loader.")

    # ---- Loaders ----
    train_loader = DataLoader(train_set, batch_size=batch_size, sampler=sampler, drop_last=True)
    val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False, drop_last=False)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False, drop_last=False)

    return train_loader, val_loader, test_loader
