def load_obj(filename):
    vertices = []
    faces = []

    try:
        with open(filename, "r") as f:
            for line in f:
                if line.startswith("v "):
                    parts = line.strip().split()
                    try:
                        vertex = tuple(float(p) for p in parts[1:4])
                        vertices.append(vertex)
                    except ValueError:
                        print(f"Skipping malformed vertex line: {line.strip()}")
                elif line.startswith("f "):
                    parts = line.strip().split()
                    face = []
                    for p in parts[1:]:
                        try:
                            vertex_index = int(p.split("/")[0]) - 1
                            face.append(vertex_index)
                        except ValueError:
                            print(f"Skipping malformed face line: {line.strip()}")
                            face = []
                            break
                    # Triangulate if face has more than 3 vertices
                    if len(face) == 3:
                        faces.append(face)
                    elif len(face) > 3:
                        for i in range(1, len(face) - 1):
                            faces.append([face[0], face[i], face[i + 1]])

    except FileNotFoundError:
        print(f"Error: File not found at {filename}")
        return [], []  # Return empty lists to indicate failure.
    except Exception as e:
        print(f"An error occurred while loading the file: {e}")
        return [], []
    return vertices, faces
