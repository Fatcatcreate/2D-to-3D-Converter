import numpy as np
import open3d as o3d
import cv2
import os
from skimage import measure

def load_and_process_images(image_paths):
    processed_images = {}
    dimensions = {}
    for view, path in image_paths.items():
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Could not load image at {path}")
        
        # Store dimensions
        height, width = img.shape[:2]
        dimensions[view] = {'height': height, 'width': width}
    width_x = max(dimensions['front']['width'], dimensions['back']['width'], 
                  dimensions['top']['width'], dimensions['bottom']['width'])
    height_y = max(dimensions['front']['height'], dimensions['back']['height'],
                   dimensions['left']['height'], dimensions['right']['height'])
    depth_z = max(dimensions['left']['width'], dimensions['right']['width'],
                  dimensions['top']['height'], dimensions['bottom']['height'])
    processed_images['dimensions'] = {
        'width': width_x,  
        'height': height_y,  
        'depth': depth_z    
    }
    
    for view, path in image_paths.items():
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply some preprocessing to get a clean binary image
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        kernel = np.ones((5, 5), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        processed_images[view] = binary
        cv2.imwrite(f"binary_{view}.png", binary)
    
    return processed_images

def create_voxel_grid(processed_images, resolution=100):
    voxel_grid = np.ones((resolution, resolution, resolution), dtype=bool)
    # Create coordinate grids
    x = np.linspace(-1, 1, resolution)
    y = np.linspace(-1, 1, resolution)
    z = np.linspace(-1, 1, resolution)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    coords = np.stack([X.flatten(), Y.flatten(), Z.flatten()], axis=1)
    
    if 'front' in processed_images:
        front_img = processed_images['front']
        h, w = front_img.shape
        points_2d = np.zeros((coords.shape[0], 2))
        points_2d[:, 0] = (coords[:, 1] + 1) / 2 * (h - 1)  
        points_2d[:, 1] = (1 - coords[:, 2]) / 2 * (w - 1)  
        points_2d = np.round(points_2d).astype(int)
        
        valid_indices = (points_2d[:, 0] >= 0) & (points_2d[:, 0] < h) & \
                        (points_2d[:, 1] >= 0) & (points_2d[:, 1] < w)
        outside_indices = np.zeros(coords.shape[0], dtype=bool)
        outside_indices[valid_indices] = front_img[points_2d[valid_indices, 0], points_2d[valid_indices, 1]] == 0
        
        voxel_grid_flat = voxel_grid.flatten()
        voxel_grid_flat[outside_indices] = False
        voxel_grid = voxel_grid_flat.reshape(voxel_grid.shape)
    
    if 'back' in processed_images:
        back_img = processed_images['back']
        h, w = back_img.shape
        points_2d = np.zeros((coords.shape[0], 2))
        points_2d[:, 0] = (coords[:, 1] + 1) / 2 * (h - 1)  
        points_2d[:, 1] = (1 - coords[:, 2]) / 2 * (w - 1)  
        points_2d = np.round(points_2d).astype(int)
        
        valid_indices = (points_2d[:, 0] >= 0) & (points_2d[:, 0] < h) & \
                        (points_2d[:, 1] >= 0) & (points_2d[:, 1] < w)
        
        outside_indices = np.zeros(coords.shape[0], dtype=bool)
        outside_indices[valid_indices] = back_img[points_2d[valid_indices, 0], points_2d[valid_indices, 1]] == 0
        voxel_grid_flat = voxel_grid.flatten()
        voxel_grid_flat[outside_indices] = False
        voxel_grid = voxel_grid_flat.reshape(voxel_grid.shape)
    
    if 'top' in processed_images:
        top_img = processed_images['top']
        h, w = top_img.shape
        
        points_2d = np.zeros((coords.shape[0], 2))
        points_2d[:, 0] = (coords[:, 0] + 1) / 2 * (w - 1)  
        points_2d[:, 1] = (1 - coords[:, 2]) / 2 * (h - 1)  
        points_2d = np.round(points_2d).astype(int)
        
        valid_indices = (points_2d[:, 0] >= 0) & (points_2d[:, 0] < w) & \
                        (points_2d[:, 1] >= 0) & (points_2d[:, 1] < h)
        
        outside_indices = np.zeros(coords.shape[0], dtype=bool)
        outside_indices[valid_indices] = top_img[points_2d[valid_indices, 1], points_2d[valid_indices, 0]] == 0
        
        voxel_grid_flat = voxel_grid.flatten()
        voxel_grid_flat[outside_indices] = False
        voxel_grid = voxel_grid_flat.reshape(voxel_grid.shape)
    
    if 'bottom' in processed_images:
        bottom_img = processed_images['bottom']
        h, w = bottom_img.shape
        
        points_2d = np.zeros((coords.shape[0], 2))
        points_2d[:, 0] = (coords[:, 0] + 1) / 2 * (w - 1)  
        points_2d[:, 1] = (1 - coords[:, 2]) / 2 * (h - 1)  
        points_2d = np.round(points_2d).astype(int)
        
        valid_indices = (points_2d[:, 0] >= 0) & (points_2d[:, 0] < w) & \
                        (points_2d[:, 1] >= 0) & (points_2d[:, 1] < h)
        
        outside_indices = np.zeros(coords.shape[0], dtype=bool)
        outside_indices[valid_indices] = bottom_img[points_2d[valid_indices, 1], points_2d[valid_indices, 0]] == 0
        
        voxel_grid_flat = voxel_grid.flatten()
        voxel_grid_flat[outside_indices] = False
        voxel_grid = voxel_grid_flat.reshape(voxel_grid.shape)
    
    if 'left' in processed_images:
        left_img = processed_images['left']
        h, w = left_img.shape
        
        points_2d = np.zeros((coords.shape[0], 2))
        points_2d[:, 0] = (coords[:, 1] + 1) / 2 * (h - 1)  
        points_2d[:, 1] = (coords[:, 0] + 1) / 2 * (w - 1)  
        points_2d = np.round(points_2d).astype(int)
        
        valid_indices = (points_2d[:, 0] >= 0) & (points_2d[:, 0] < h) & \
                        (points_2d[:, 1] >= 0) & (points_2d[:, 1] < w)
        
        outside_indices = np.zeros(coords.shape[0], dtype=bool)
        outside_indices[valid_indices] = left_img[points_2d[valid_indices, 0], points_2d[valid_indices, 1]] == 0
        voxel_grid_flat = voxel_grid.flatten()
        voxel_grid_flat[outside_indices] = False
        voxel_grid = voxel_grid_flat.reshape(voxel_grid.shape)
    
    if 'right' in processed_images:
        right_img = processed_images['right']
        h, w = right_img.shape
        
        points_2d = np.zeros((coords.shape[0], 2))
        points_2d[:, 0] = (coords[:, 1] + 1) / 2 * (h - 1) 
        points_2d[:, 1] = (coords[:, 0] + 1) / 2 * (w - 1)  
        points_2d = np.round(points_2d).astype(int)
        
        valid_indices = (points_2d[:, 0] >= 0) & (points_2d[:, 0] < h) & \
                        (points_2d[:, 1] >= 0) & (points_2d[:, 1] < w)
        
        outside_indices = np.zeros(coords.shape[0], dtype=bool)
        outside_indices[valid_indices] = right_img[points_2d[valid_indices, 0], points_2d[valid_indices, 1]] == 0
        voxel_grid_flat = voxel_grid.flatten()
        voxel_grid_flat[outside_indices] = False
        voxel_grid = voxel_grid_flat.reshape(voxel_grid.shape)
    
    return voxel_grid

def create_mesh_from_voxels(voxel_grid):
    voxel_grid_float = voxel_grid.astype(float)
    
    # Apply marching cubes
    print("Voxel Grid Float Min:", voxel_grid_float.min())
    print("Voxel Grid Float Max:", voxel_grid_float.max())

    verts, faces, normals, _ = measure.marching_cubes(voxel_grid_float, level=0.5)
    
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(verts)
    mesh.triangles = o3d.utility.Vector3iVector(faces)
    mesh.vertex_normals = o3d.utility.Vector3dVector(normals)
    voxel_size = voxel_grid.shape[0]
    verts_scaled = np.asarray(mesh.vertices)
    verts_scaled = (verts_scaled / voxel_size) * 2 - 1
    mesh.vertices = o3d.utility.Vector3dVector(verts_scaled)
    
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()
    
    return mesh

def create_voxel_visualisation(voxel_grid, output_dir):

    voxel_coords = np.argwhere(voxel_grid)
    
    size = voxel_grid.shape[0]
    voxel_coords = voxel_coords / size * 2 - 1
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(voxel_coords)
    
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    
    vis.add_geometry(pcd)
    
    opt = vis.get_render_option()
    opt.point_size = 3.0
    opt.background_color = np.array([0.1, 0.1, 0.1])
    
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image(os.path.join(output_dir, "voxel_visualisation.png"))
    
    vis.run()
    vis.destroy_window()

def visualise_and_save(mesh, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    o3d.io.write_triangle_mesh(os.path.join(output_dir, "mesh.obj"), mesh)
    
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(mesh)
    
    opt = vis.get_render_option()
    opt.mesh_show_wireframe = False
    opt.mesh_show_back_face = True
    opt.background_color = np.array([0.1, 0.1, 0.1])
    
    vis.get_render_option().light_on = True
    
    views = [
        {"front": [0, 0, -1], "up": [0, -1, 0]},
        {"front": [1, 0, 0], "up": [0, -1, 0]},
        {"front": [0, -1, 0], "up": [0, 0, -1]},
        {"front": [-1, -1, -1], "up": [0, -1, 0]}
    ]
    
    vis.update_geometry(mesh)
    for i, view in enumerate(views):
        ctr = vis.get_view_control()
        ctr.set_front(view["front"])
        ctr.set_lookat([0, 0, 0])
        ctr.set_up(view["up"])
        ctr.set_zoom(0.8)
        
        vis.poll_events()
        vis.update_renderer()
        vis.capture_screen_image(os.path.join(output_dir, f"view_{i+1}.png"))
    
    print(f"Rendering interactive visualisation. Close the window to continue...")
    vis.run()
    vis.destroy_window()

def main(image_paths, output_dir, voxel_resolution=100):

    print("Step 1: Loading and processing images...")
    processed_images = load_and_process_images(image_paths)
    
    print("Step 2: Creating voxel grid using visual hull technique...")
    voxel_grid = create_voxel_grid(processed_images, resolution=voxel_resolution)
    
    print(f"Voxel grid created with shape: {voxel_grid.shape}")
    print(f"Number of filled voxels: {np.sum(voxel_grid)}")
    
    print("Creating voxel visualisation for debugging...")
    create_voxel_visualisation(voxel_grid, output_dir)
    
    print("Step 3: Converting voxel grid to mesh using Marching Cubes...")
    mesh = create_mesh_from_voxels(voxel_grid)
    
    print(f"Mesh created with {len(mesh.vertices)} vertices and {len(mesh.triangles)} triangles")
    
    print("Step 4: Visualising and saving results...")
    visualise_and_save(mesh, output_dir)
    
    print(f"3D reconstruction complete. Results saved to {output_dir}")
    print(f"Mesh saved as: {os.path.join(output_dir, 'mesh.obj')}")
    print(f"Visualisations saved as: {os.path.join(output_dir, 'view_*.png')}")

if __name__ == "__main__":
    image_paths = {
        'front': 'test_images/bonsai_tree/front.png',
        'back': 'test_images/bonsai_tree/back.png',
        'top': 'test_images/bonsai_tree/top.png',
        'bottom': 'test_images/bonsai_tree/bottom.png',
        'left': 'test_images/bonsai_tree/left.png',
        'right': 'test_images/bonsai_tree/right.png'
    }
    output_dir = "reconstruction_output"
    
    # Adjust voxel resolution as needed
    # Higher resolution = more details but more memory and computation time
    voxel_resolution = 100 
    main(image_paths, output_dir, voxel_resolution=voxel_resolution)
