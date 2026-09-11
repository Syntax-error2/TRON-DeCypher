from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class HillDecoder(DecoderBase):
    name = "Hill Cipher"
    category = "classical_ciphers"
    description = "Polygraphic substitution using matrix multiplication."
    expected_params = {
        "matrix": {"type": "str", "default": "2,3,5,7", "description": "Comma-separated matrix values (e.g., 2,3,5,7 for 2x2 or 9 vals for 3x3)"},
        "mode": {"type": "str", "default": "decrypt", "description": "encrypt or decrypt"}
    }
    
    def _mod_inverse(self, a: int, m: int) -> int | None:
        a = a % m
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        return None
        
    def _invert_matrix_2x2(self, mat: list[int]) -> list[int] | None:
        det = (mat[0]*mat[3] - mat[1]*mat[2]) % 26
        inv_det = self._mod_inverse(det, 26)
        if inv_det is None:
            return None
        return [
            (mat[3] * inv_det) % 26,
            (-mat[1] * inv_det) % 26,
            (-mat[2] * inv_det) % 26,
            (mat[0] * inv_det) % 26
        ]
        
    def _invert_matrix_3x3(self, mat: list[int]) -> list[int] | None:
        # A B C
        # D E F
        # G H I
        m00, m01, m02 = mat[0], mat[1], mat[2]
        m10, m11, m12 = mat[3], mat[4], mat[5]
        m20, m21, m22 = mat[6], mat[7], mat[8]
        
        det = (m00*(m11*m22 - m12*m21) - m01*(m10*m22 - m12*m20) + m02*(m10*m21 - m11*m20)) % 26
        inv_det = self._mod_inverse(det, 26)
        if inv_det is None:
            return None
            
        return [
            ((m11*m22 - m12*m21) * inv_det) % 26,
            (-(m01*m22 - m02*m21) * inv_det) % 26,
            ((m01*m12 - m02*m11) * inv_det) % 26,
            (-(m10*m22 - m12*m20) * inv_det) % 26,
            ((m00*m22 - m02*m20) * inv_det) % 26,
            (-(m00*m12 - m02*m10) * inv_det) % 26,
            ((m10*m21 - m11*m20) * inv_det) % 26,
            (-(m00*m21 - m01*m20) * inv_det) % 26,
            ((m00*m11 - m01*m10) * inv_det) % 26
        ]

    def _transform(self, text: str, mat: list[int], size: int) -> str:
        text_clean = [ord(c.upper()) - ord('A') for c in text if c.isalpha()]
        
        # Pad if needed
        while len(text_clean) % size != 0:
            text_clean.append(ord('X') - ord('A'))
            
        result = []
        for i in range(0, len(text_clean), size):
            block = text_clean[i:i+size]
            if size == 2:
                r1 = (mat[0]*block[0] + mat[1]*block[1]) % 26
                r2 = (mat[2]*block[0] + mat[3]*block[1]) % 26
                result.extend([chr(r1 + ord('A')), chr(r2 + ord('A'))])
            elif size == 3:
                r1 = (mat[0]*block[0] + mat[1]*block[1] + mat[2]*block[2]) % 26
                r2 = (mat[3]*block[0] + mat[4]*block[1] + mat[5]*block[2]) % 26
                r3 = (mat[6]*block[0] + mat[7]*block[1] + mat[8]*block[2]) % 26
                result.extend([chr(r1 + ord('A')), chr(r2 + ord('A')), chr(r3 + ord('A'))])
                
        return "".join(result)

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        mat_str = context.get("matrix", "2,3,5,7")
        mode = context.get("mode", "decrypt")
        decrypt = mode.lower() != "encrypt"
        
        try:
            mat = [int(x.strip()) for x in mat_str.split(",")]
        except ValueError:
            return self._create_result(False, errors=["Matrix must be comma-separated integers"])
            
        if len(mat) == 4:
            size = 2
        elif len(mat) == 9:
            size = 3
        else:
            return self._create_result(False, errors=["Only 2x2 (4 elements) or 3x3 (9 elements) matrices are supported."])
            
        if decrypt:
            if size == 2:
                inv_mat = self._invert_matrix_2x2(mat)
            else:
                inv_mat = self._invert_matrix_3x3(mat)
                
            if inv_mat is None:
                return self._create_result(False, errors=["Matrix is not invertible modulo 26."])
            mat = inv_mat
            
        dec = self._transform(text, mat, size)
        return self._create_result(True, output_text=dec)

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.05, {"reason": "Hill Cipher detection relies on known plaintext."}
