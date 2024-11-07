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
    """Build a Huffman tree and encode the message."""
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
    """Decode a binary-encoded string using the Huffman tree."""
    reverse_tree = {v: k for k, v in tree.items()}
    decoded_msg = bytearray()
    current_code = ""
    for bit in encoded_str:
        current_code += bit
        if current_code in reverse_tree:
            decoded_msg.append(reverse_tree[current_code])
            current_code = ""
    return bytes(decoded_msg)


def compress(msg):
    """Compress the message and return binary compressed data."""
    encoded_msg, tree = code(msg)
    padding = (8 - len(encoded_msg) % 8) % 8
    encoded_msg += '0' * padding

    compressed_data = array.array('B')
    for i in range(0, len(encoded_msg), 8):
        byte = int(encoded_msg[i:i + 8], 2)
        compressed_data.append(byte)

    tree['pad'] = padding
    return compressed_data, tree



def decompress(bitstring, tree):
    """Decompress the binary bitstring using the Huffman tree."""
    padding = tree.pop('pad', 0)
    bit_str = ''.join(f"{byte:08b}" for byte in bitstring)[:-padding]
    return decode(bit_str, tree)



def usage():
    sys.stderr.write("Usage: {} [-c|-d|-v|-w] infile outfile\n".format(sys.argv[0]))
    exit(1)

if __name__=='__main__':
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
        fp = open(infile, 'rb')
        msg = fp.read()
        fp.close()
        if compressing:
            compr, tree = compress(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), compr), fcompressed)
            fcompressed.close()
        else:
            enc, tree = code(msg)
            print(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), enc), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pickleRick, compr = marshal.load(fp)
        tree = pickle.loads(pickleRick)
        fp.close()
        if decompressing:
            msg = decompress(compr, tree)
        else:
            msg = decode(compr, tree)
            print(msg)
        fp = open(outfile, 'wb')
        fp.write(msg)
        fp.close()