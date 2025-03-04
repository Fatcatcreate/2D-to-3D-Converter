# 3D Converter - A Visual Hull-Based 3D Reconstruction Tool

## Overview

This project is a **3D reconstruction tool** that generates a 3D mesh from six orthographic images using the **visual hull technique**. It takes six images representing different views (front, back, left, right, top, and bottom) and constructs a **voxel grid**, which is then converted into a 3D mesh using the **Marching Cubes algorithm**.

This tool is useful for approximating 3D objects from 2D silhouettes and can be applied to **computer vision, AI-generated assets, and digital reconstruction** projects.

---

## How It Works

### 1. **Image Processing**
- The script loads six images from the `test_images/` directory.
- Each image is converted to grayscale and binarised (black & white) to extract object silhouettes.
- Morphological operations (closing and opening) are applied to clean up the binary images.

### 2. **Voxel Grid Creation**
- A **3D voxel grid** is initialised (default: `100x100x100`).
- Each voxel is projected onto the six binary images.
- If a voxel is inside all silhouettes, it is kept; otherwise, it is removed.

### 3. **Mesh Generation (Marching Cubes)**
- The voxel grid is converted into a **triangle mesh** using the **Marching Cubes algorithm**, which extracts a smooth surface from the voxelised representation.
- Post-processing steps include:
  - Removing degenerate and duplicate triangles.
  - Fixing non-manifold edges for a clean mesh.

### 4. **Visualisation and Output**
- The mesh is saved as `mesh.obj`.
- Multiple viewpoint renders (`view_1.png`, `view_2.png`, etc.) are generated.
- An interactive Open3D visualiser allows for real-time exploration.

---

## How to Upload Your Drawings

### **1. Capture a High-Contrast Black & White Image**
- Use a **camera or scanner** to capture your drawing.
- Ensure the image is **black and white** with high contrast (no greyscale or shadows).

### **2. Resize for Best Results**
- Resize the image to **256x256 pixels** to match the input requirements.
- Use an image editor or a script (`OpenCV` or `Pillow` in Python) to do this.

### **3. Save in the Correct Format**
- Save the processed image as a `.png` file.
- Place it in the `test_images/` directory with the appropriate name (`front.png`, `back.png`, etc.).

---

## Installation & Setup

### **1. Clone the Repository**
```sh
git clone https://github.com/Fatcatcreate/2dimages_to_3d-converter.git
cd 3d-converter
```

### **2. Install Dependencies**
There is no `requirements.txt`, so install the required packages manually:
```sh
pip install numpy open3d opencv-python-headless scikit-image
```

### **3. Prepare Input Images**
- Ensure six silhouette images exist under `test_images/OBJECT_FILE/` with names:
  - `front.png`, `back.png`, `left.png`, `right.png`, `top.png`, `bottom.png`

### **4. Run the Script**
```sh
python 3d_converter.py
```

- Output files will be saved to `reconstruction_output/`
- Open `mesh.obj` in a 3D viewer or Blender.

---

## Future Improvements

### **More Robust Image Preprocessing**
- Implement adaptive thresholding for silhouette extraction.
- Use deep learning (e.g., U-Net) for segmentation.

### **Higher-Resolution Voxel Grid**
- Implement an **octree-based** voxel structure to reduce memory usage.
- Support for **multi-resolution meshes**.

### **Better Visualisation**
- Add **textured rendering**.
- Improve Open3D visualisation with lighting and material effects.

### **STL Export for 3D Printing**
- Add support for exporting in `.stl` format for 3D printing applications.

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-xyz`).
3. Commit your changes (`git commit -m "Added feature xyz"`).
4. Push to your branch (`git push origin feature-xyz`).
5. Submit a pull request.

For major changes, please open an issue first to discuss your proposal.

