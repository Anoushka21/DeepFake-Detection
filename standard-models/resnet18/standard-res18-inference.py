import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from PIL import Image
from tqdm import tqdm

device = 'cuda' if torch.cuda.is_available() else 'cpu'

class DeepfakeDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        label = torch.tensor(self.labels[idx], dtype=torch.float32)

        return image, label

def load_images(directory, label):
    images = []
    labels = []
    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):
            img_path = os.path.join(directory, filename)
            images.append(img_path)
            labels.append(label)
    return images, labels

def main():
    ROOT_DIRECTORY = "/scratch/am13018/"

    # Load deepfake and real images
    test_deepfake_dir = ROOT_DIRECTORY+"real_vs_fake/real-vs-fake/test/fake/"
    test_real_dir = ROOT_DIRECTORY+"real_vs_fake/real-vs-fake/test/real"

    deepfake_images, deepfake_labels = load_images(test_deepfake_dir, label=1)
    real_images, real_labels = load_images(test_real_dir, label=0)

    # Combine deepfake and real images
    all_test_images = deepfake_images + real_images
    all_test_labels = deepfake_labels + real_labels

    label_encoder = LabelEncoder()
    all_labels_encoded = label_encoder.fit_transform(all_test_labels)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    test_dataset = DeepfakeDataset(all_test_images, all_labels_encoded, transform=transform)

    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=True, num_workers=4)

    model = models.resnet18()
    model.fc = nn.Linear(model.fc.in_features, 1)
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.00001, weight_decay=1e-5, eps=1e-7)

    checkpoint_filepath='/scratch/am13018/checkp_res18_norm/best_model_27.pth'
    checkpoint = torch.load(checkpoint_filepath)

    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    model.to(device)
    print(f"Using {device}")
    print("Testing started")
    with torch.no_grad():
        model.eval()
        test_correct=0
        for image,target in tqdm(test_loader):
            image,target = image.to(device),target.to(device)
            target = target.unsqueeze(1)
            outputs = torch.sigmoid(model(image))
            test_correct += torch.sum((outputs > 0.5) == target)

    print(f'Test accuracy:{test_correct /len(test_loader.dataset)}')

if __name__=="__main__":
    main()
