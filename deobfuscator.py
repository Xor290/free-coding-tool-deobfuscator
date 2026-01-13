import ast
import base64
import os
import zlib
from pathlib import Path


class ByteStringFinder(ast.NodeVisitor):
    def __init__(self):
        self.results = []

    def visit_Constant(self, node):
        if isinstance(node.value, bytes):
            self.results.append(node.value)
        self.generic_visit(node)


def load_file(file_path):
    with open(file_path, "rb") as f:
        return f.read()


def extract_payload(surface_code: bytes, layer_num: int = 0) -> bytes:
    try:
        debug_path = Path(f"layer_{layer_num:03d}.py")
        with open(debug_path, "wb") as f:
            f.write(surface_code)

        try:
            code_str = surface_code.decode("utf-8")
        except UnicodeDecodeError:
            code_str = surface_code.decode("latin-1")

        tree = ast.parse(code_str)
    except SyntaxError as exc:
        print(f"  Syntax error: {exc}")
        print(f"  Content preview: {surface_code[:500]}")
        raise ValueError(f"Invalid Python syntax: {exc}")

    bsf = ByteStringFinder()
    bsf.visit(tree)

    if len(bsf.results) > 1:
        return bsf.results[0]
    elif not bsf.results:
        raise ValueError("No byte string found in the code")
    else:
        return bsf.results[0]


def deobfuscate_layer(payload: bytes) -> bytes:
    try:
        reversed_payload = payload[::-1]
        decoded = base64.b64decode(reversed_payload)
        decompressed = zlib.decompress(decoded)
        return decompressed
    except Exception as e:
        raise ValueError(f"Deobfuscation failed: {e}")


if __name__ == "__main__":
    try:
        payload_bytes = load_file(Path("obf_payload.py"))

        current_payload = extract_payload(payload_bytes, layer_num=0)

        max_layers = 100
        for layer in range(max_layers):
            try:
                deobfuscated = deobfuscate_layer(current_payload)

                try:
                    current_payload = extract_payload(deobfuscated, layer_num=layer + 1)
                except ValueError as e:
                    print(f"\n{'=' * 60}")
                    print(f"Final payload reached at layer {layer + 1}")
                    print(f"{'=' * 60}\n")

                    output_path = Path("deobfuscated_payload.py")
                    with open(output_path, "wb") as f:
                        f.write(deobfuscated)

                    print(f"Success! Deobfuscated payload saved to: {output_path}")
                    print(f"Final size: {len(deobfuscated)} bytes")

                    try:
                        preview = deobfuscated.decode("utf-8")
                        print(f"\n{'=' * 60}")
                        print("Full deobfuscated content:")
                        print(f"{'=' * 60}\n")
                        print(preview)
                    except:
                        print("(Binary content - cannot preview)")

                    break

            except Exception as e:
                print(f"\nError at layer {layer + 1}: {e}")
                import traceback

                traceback.print_exc()
                break
        else:
            print(f"Warning: Reached max layers ({max_layers})")

    except FileNotFoundError:
        print("Error: obf_payload.py not found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
