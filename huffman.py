import os
import sys
import marshal
import array
import heapq

try:
    import cPickle as pickle
except ImportError:
    import pickle

def code(msg):
    freqs = {}
    for char in msg:
        freqs[char] = freqs.get(char, 0) + 1

    heap = [[weight, [char, ""]] for char, weight in freqs.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    huffman_tree = {char: code for char, code in heap[0][1:]}

    encoded_msg = ''.join(huffman_tree[char] for char in msg)
    return encoded_msg, huffman_tree

def decode(encoded_str, tree):
    reverse_tree = {v: k for k, v in tree.items()}
    decoded_msg = ""
    current_code = ""
    for bit in encoded_str:
        current_code += bit
        if current_code in reverse_tree:
            decoded_msg += reverse_tree[current_code]
            current_code = ""
    return decoded_msg

def compress(msg):
    encoded_msg, tree = code(msg)
    padding = 8 - len(encoded_msg) % 8
    encoded_msg += '0' * padding

    compressed_data = array.array('B')
    for i in range(0, len(encoded_msg), 8):
        byte = int(encoded_msg[i:i + 8], 2)
        compressed_data.append(byte)

    tree['pad'] = padding
    return compressed_data, tree

def decompress(bitstring, tree):
    padding = tree.pop('pad', 0)  # Retrieve padding information
    bit_str = ''.join(f"{byte:08b}" for byte in bitstring)[:-padding]
    return decode(bit_str, tree)

def usage():
    sys.stderr.write("Usage: {} [-c|-d|-v|-w] infile outfile\n".format(sys.argv[0]))
    exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        usage()
    opt = sys.argv[1]
    compressing = False
    decompressing = False
    encoding = False
    decoding = False
    if opt == "-c":
        compressing = True
    elif opt == "-d":
        decompressing = True
    elif opt == "-v":
        encoding = True
    elif opt == "-w":
        decoding = True
    else:
        usage()

    infile = sys.argv[2]
    outfile = sys.argv[3]
    assert os.path.exists(infile)

    if compressing or encoding:
        with open(infile, 'rb') as fp:
            msg = fp.read().decode('utf-8')
        if compressing:
            compressed_data, tree = compress(msg)
            with open(outfile, 'wb') as fcompressed:
                marshal.dump((pickle.dumps(tree), compressed_data), fcompressed)
        else:
            encoded_msg, tree = code(msg)
            print(encoded_msg)
            with open(outfile, 'wb') as fcompressed:
                marshal.dump((pickle.dumps(tree), encoded_msg), fcompressed)
    else:
        with open(infile, 'rb') as fp:
            pickled_tree, data = marshal.load(fp)
            tree = pickle.loads(pickled_tree)
        if decompressing:
            msg = decompress(data, tree)
            with open(outfile, 'w') as fdecompressed:
                fdecompressed.write(msg)
        else:
            decoded_msg = decode(data, tree)
            print(decoded_msg)
            with open(outfile, 'w') as fdecoded:
                fdecoded.write(decoded_msg)
