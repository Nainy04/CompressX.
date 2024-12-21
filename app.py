from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
import heapq
from collections import defaultdict

app = Flask(__name__)

# Configure upload and compressed directories
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER

# Ensure upload and compressed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

# Huffman coding implementation
class HuffmanNode:
    def _init_(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def _lt_(self, other):
        return self.freq < other.freq

def build_huffman_tree(frequency):
    heap = [HuffmanNode(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = HuffmanNode(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)

    return heap[0]

def build_huffman_codes(root):
    codes = {}

    def generate_codes(node, current_code):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = current_code
            return
        generate_codes(node.left, current_code + "0")
        generate_codes(node.right, current_code + "1")

    generate_codes(root, "")
    return codes

def huffman_compress(input_path, output_path):
    try:
        with open(input_path, 'r') as file:
            content = file.read()

        if not content:
            raise ValueError("Input file is empty")

        frequency = defaultdict(int)
        for char in content:
            frequency[char] += 1

        root = build_huffman_tree(frequency)
        huffman_codes = build_huffman_codes(root)

        compressed_content = "".join(huffman_codes[char] for char in content)

        with open(output_path, 'w') as compressed_file:
            compressed_file.write(compressed_content)
        print(f"Huffman compression completed: {output_path}")
    except Exception as e:
        raise RuntimeError(f"Huffman compression failed: {e}")

# Improved RLE implementation
def rle_compress(data):
    if not data:
        raise ValueError("No data to compress")

    compressed = []
    prev_char = ""
    count = 1

    for char in data:
        if char == prev_char:
            count += 1
        else:
            if prev_char:
                compressed.append(f"{prev_char}{count}")
            prev_char = char
            count = 1

    if prev_char:
        compressed.append(f"{prev_char}{count}")

    return "".join(compressed)

def jpeg_compress(input_path, output_path):
    try:
        with open(input_path, 'rb') as file:
            content = file.read()

        if not content:
            raise ValueError("Input file is empty")

        compressed_content = rle_compress(content.decode('latin1'))

        with open(output_path, 'wb') as compressed_file:
            compressed_file.write(compressed_content.encode('latin1'))
        print(f"JPEG compression completed: {output_path}")
    except Exception as e:
        raise RuntimeError(f"JPEG compression failed: {e}")

def png_compress(input_path, output_path):
    try:
        with open(input_path, 'rb') as file:
            content = file.read()

        if not content:
            raise ValueError("Input file is empty")

        compressed_content = rle_compress(content.decode('latin1'))

        with open(output_path, 'wb') as compressed_file:
            compressed_file.write(compressed_content.encode('latin1'))
        print(f"PNG compression completed: {output_path}")
    except Exception as e:
        raise RuntimeError(f"PNG compression failed: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    allowed_ext = {'png': png_compress, 'jpg': jpeg_compress, 'txt': huffman_compress}

    if file:
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext in allowed_ext:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"File saved: {filepath}")

            compressed_filename = f"compressed_{filename}"
            compressed_filepath = os.path.join(app.config['COMPRESSED_FOLDER'], compressed_filename)

            try:
                print(f"Starting {ext.upper()} compression...")
                allowed_ext[ext](filepath, compressed_filepath)
                print(f"File compressed successfully: {compressed_filepath}")
            except Exception as e:
                print(f"Error during compression: {e}")
                return 'Compression failed'

            if not os.path.exists(compressed_filepath):
                print("Error: Compressed file not found")
                return 'Compression failed, file not created'

            return redirect(url_for('download', filename=compressed_filename))
        else:
            return 'File type not supported'

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(app.config['COMPRESSED_FOLDER'], filename)
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found for download")
        return 'File not found'
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
