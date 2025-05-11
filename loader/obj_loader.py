def load_obj(filename):
    vertices = []
    faces = []

    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('v '):
                    parts = line.strip().split()
                    try:
                        vertex = tuple(float(p) for p in parts[1:4])
                        vertices.append(vertex)
                    except ValueError:
                        print(f"Skipping malformed vertex line: {line.strip()}")
                elif line.startswith('f '):
                    parts = line.strip().split()
                    # Handle different number of vertices per face.
                    face = []
                    for p in parts[1:]:
                        try:
                            #  Handles vertex/texture/normal indices
                            vertex_index = int(p.split('/')[0]) - 1
                            face.append(vertex_index)
                        except ValueError:
                            print(f"Skipping malformed face line: {line.strip()}")
                            face = [] # Clear the face if there is an error.
                            break
                    if face: # only add the face if it is not empty
                        faces.append(face)
    except FileNotFoundError:
        print(f"Error: File not found at {filename}")
        return [], []  # Return empty lists to indicate failure.
    except Exception as e:
        print(f"An error occurred while loading the file: {e}")
        return [], []
    return vertices, faces


# def main():

#     filename = "obj_file_expl/FinalBaseMesh.obj"  # Changed to a raw string
#     vertices, faces = load_obj(filename)

#     if vertices and faces: # Check if load_obj was successful
#         print(f"Loaded {filename} successfully.")
#         print(f"Number of vertices: {len(vertices)}")
#         print(f"Number of faces: {len(faces)}")

#         # Print the first 5 vertices
#         print("\nFirst 5 vertices:")
#         for i, vertex in enumerate(vertices[:5]):
#             print(f"  {i+1}: {vertex}")

#         # Print the first 5 faces
#         print("\nFirst 5 faces:")
#         for i, face in enumerate(faces[:5]):
#             #  Adjust the indices for display (add 1)
#             display_face = [index + 1 for index in face]
#             print(f"  {i+1}: {display_face}")
#     else:
#         print(f"Failed to load {filename}.")

# if __name__ == "__main__":
#     main()
