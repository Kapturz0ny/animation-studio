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
                    # Handle different number of vertices per face
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
