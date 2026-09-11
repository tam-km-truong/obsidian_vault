From a discussion with Tam who was looking for paper about compressors, there are some recap papers on dictionary-based compressors, here are some assertions about some of them (none of compressors have a single official publication)

To improve compression, all following algorithm can increase their sliding window to catch further redundancies and may have some extra features. Increasing the sliding window size will also increase compression time and the gain won't necessarily be worth the extra time required.

How it works, it could be roughly summed up in 2 steps:

    Find a redundancy, note where it was previously seen.

Entropy-coding

Gzip: Deflate (LZ77 + Huffman coding)

    Midrange compression speed (default compression: 70 MB/s, max compression: 7-10 MB/s)

Good decompression speed (300 MB/s)Midrange compression capabilityBalanced between compression strength and time but is a bit obselete du to new compressors (most likely due to Zstd)

XZ: LZMA (LZ77 + Markov Chain)

    Low compression speed (default compression: 5 MB/s, max compression: 1-2 MB/s)

Low decompression speed (100 MB/s)High compression capabilityIt has a larger sliding window than most of dictionary-based compressor. and generally provides best compression.

Zstd: (LZ77 + Asymetrical Numeral System)

    High compression speed (default compression: 700 MB/s, max compression: 8-10 MB/s)

Very high decompression speed (1 GB/s)Midrange compression capabilityKilled Gzip. For same compression ratio, Zstd is 10 times faster than Gzip. Low sliding window size (by default but can be increased)

LZ4 (same than Zstd but optimized with even lower sliding window size): 

    High compression speed (700-1000 MB/s)

Very high decompression speed (almost = memcpy)Poor compression capabilityNot designed for archiving purpose