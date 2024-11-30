def get_file_extension(file_bytes):
    if file_bytes.startswith(b"\xff\xd8\xff\xee") or file_bytes.startswith(b"\xff\xd8\xff\xdb") or file_bytes.startswith(b"\xff\xd8\xff\xe0") or file_bytes.startswith(b"\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01") or (file_bytes[:4]==b"\xff\xd8\xff\xe1" and file_bytes[6:12]==b"\x45\x78\x69\x66\x00\x00"):
        return "jpg"
    elif file_bytes.startswith(b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"):
        return "png"
    elif file_bytes.startswith(b"\x47\x49\x46\x38\x37\x61") or file_bytes.startswith(b"\x47\x49\x46\x38\x39\x61"):
        return "gif"
    elif file_bytes[4:12] == b"\x66\x74\x79\x70\x69\x73\x6f\x6d" or file_bytes[4:12] == b"\x66\x74\x79\x70\x4d\x53\x4e\x56" or file_bytes[4:12] == b"\x66\x74\x79\x70\x6d\x70\x34\x32":
        return "mp4"
    else:
        return None