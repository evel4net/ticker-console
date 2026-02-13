import os

"""
MATH UTILS
"""

def modinv(a: int, m: int) -> int:
    a %= m
    if a == 0:
        raise ZeroDivisionError("inverse of 0 does not exist")
    lm, hm = 1, 0
    low, high = a, m
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % m


# https://github.com/darkwallet/python-obelisk/blob/5812ccfd78a66963f7238d9835607908a8c8f392/obelisk/numbertheory.py
def modsqrt(a: int, p: int) -> int | None:
    """
    Find a quadratic residue (mod p) of 'a'.
    Solve the congruence of the form: x^2 = a (mod p).
    And returns x. Note that p - x is also a root.
    None is returned if no square root exists for these a and p.
    The Tonelli-Shanks algorithm is used (except for some simple
    cases in which the solution is known from an identity).
    This algorithm runs in polynomial time (unless the generalized
    Riemann hypothesis is false).
    """
    a = a % p
    # Simple cases
    #
    if a == 0:
        return 0
    elif p == 2:
        return a  # 1
    elif legendre_symbol(a, p) == -1:
        return None
    elif p % 4 == 3:
        return pow(a, (p + 1) // 4, p)

    # Partition p-1 to s * 2^e for an odd s (i.e.
    # reduce all the powers of 2 from p-1)
    #
    s = p - 1
    e = 0
    while s % 2 == 0:
        # Updated by lc6chang
        # s /= 2
        s //= 2
        e += 1

    # Find some 'n' with a legendre symbol n|p = -1.
    # Shouldn't take long.
    #
    n = 2
    while legendre_symbol(n, p) != -1:
        n += 1

    # Here be dragons!
    # Read the paper "Square roots from 1; 24, 51,
    # 10 to Dan Shanks" by Ezra Brown for more
    # information
    #

    # x is a guess of the square root that gets better
    # with each iteration.
    # b is the "fudge factor" - by how much we're off
    # with the guess. The invariant x^2 = ab (mod p)
    # is maintained throughout the loop.
    # g is used for successive powers of n to update
    # both a and b
    # r is the exponent - decreases with each update
    #
    x = pow(a, (s + 1) // 2, p)
    b = pow(a, s, p)
    g = pow(n, s, p)
    r = e

    while True:
        t = b
        m = 0
        for m in range(r):
            if t == 1:
                break
            t = pow(t, 2, p)

        if m == 0:
            return x

        gs = pow(g, 2 ** (r - m - 1), p)
        g = (gs * gs) % p
        x = (x * gs) % p
        b = (b * g) % p
        r = m


def legendre_symbol(a: int, p: int) -> int:
    """
    Compute the Legendre symbol a|p using Euler's criterion.
    p is a prime, a is relatively prime to p (if p divides a, then a|p = 0).
    Returns 1 if a has a square root modulo p, -1 otherwise.
    """
    assert p != 2
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls

"""
UTILS
"""

def random_nbits_int(num_bits: int) -> int:
    assert num_bits > 0
    num_bytes = (num_bits + 7) // 8
    random_bytes = os.urandom(num_bytes)
    random_int = int.from_bytes(random_bytes, byteorder='big')
    mask = (1 << num_bits) - 1
    return random_int & mask


def random_int_exclusive(stop: int) -> int:
    """
    Generate random int in the range [1, stop).
    """
    assert stop > 1
    num_bits = stop.bit_length()
    rand = 0
    while rand < 1 or rand >= stop:
        rand = random_nbits_int(num_bits)
    return rand

"""
CURVE
"""

class Point():
    def __init__(self, curve):
        self.curve = curve

    def __neg__(self):
        return self.curve.neg_point(self)

    def __add__(self, other):
        if self.curve != other.curve:
            raise ValueError(f"{self} and {other} are on different curves.")
        return self.curve.add_point(self, other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __mul__(self, scalar: int):
        return self.curve.mul_point(scalar, self)

    def __rmul__(self, scalar: int):
        return self.__mul__(scalar)


class AffinePoint(Point):
    def __init__(self, curve, x: int, y: int):
        super().__init__(curve)
        self.x = x
        self.y = y

    def __post_init__(self):
        if not self.curve.is_on_curve(self.x, self.y):
            raise ValueError(f"{self} is not on the curve.")

    def __eq__(self, other):
        return (isinstance(other, AffinePoint) and self.curve == other.curve and self.x == other.x and self.y == other.y)

class InfinityPoint(Point):
    def __init__(self, curve):
        super().__init__(curve)

    def __eq__(self, other):
        return isinstance(other, InfinityPoint) and self.curve == other.curve


class Curve:
    def __init__(self, name: str, a: int, b: int, p: int, n: int, G_x: int, G_y: int):
        self.name = name
        self.a = a
        self.b = b
        self.p = p
        self.n = n
        self.G_x = G_x
        self.G_y = G_y

        self._O = InfinityPoint(self)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def G(self) -> AffinePoint:
        return AffinePoint(self, self.G_x, self.G_y)

    def add_point(self, P: Point, Q: Point) -> Point:
        if P == self.O:
            return Q
        if Q == self.O:
            return P
        if P == -Q:
            return self.O
        assert isinstance(P, AffinePoint) and isinstance(Q, AffinePoint)
        if P == Q:
            return self._double_affine_point(P)
        return self._add_affine_point(P, Q)

    def mul_point(self, d: int, P: Point) -> Point:
        """
        https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication
        """
        if P == self.O:
            return self.O
        if d == 0:
            return self.O

        res: Point = self.O
        is_negative_scalar = d < 0
        d = -d if is_negative_scalar else d
        tmp = P
        while d:
            if d & 0x1 == 1:
                res = self.add_point(res, tmp)
            tmp = self.add_point(tmp, tmp)
            d >>= 1
        if is_negative_scalar:
            return -res
        else:
            return res

    def neg_point(self, P: Point) -> Point:
        if P == self.O:
            return self.O
        assert isinstance(P, AffinePoint)
        return self._neg_affine_point(P)

    @property
    def O(self) -> Point:  # noqa: E743
        """
        The neutral element.
        """
        pass

    def is_on_curve(self, x: int, y: int) -> bool:
        pass

    def compute_y(self, x: int) -> int | None:
        pass

    def _add_affine_point(self, P: AffinePoint, Q: AffinePoint) -> AffinePoint:
        pass

    def _double_affine_point(self, P: AffinePoint) -> AffinePoint:
        pass

    def _neg_affine_point(self, P: AffinePoint) -> AffinePoint:
        pass


class ShortWeierstrassCurve(Curve):
    """
    y^2 = x^3 + a*x + b
    https://en.wikipedia.org/wiki/Elliptic_curve
    """

    def __init__(self, name: str, a: int, b: int, p: int, n: int, G_x: int, G_y: int):
        super().__init__(name, a, b, p, n, G_x, G_y)
        self._O = InfinityPoint(self)

    @property
    def O(self) -> Point:  # noqa: E743
        return self._O

    def is_on_curve(self, x: int, y: int) -> bool:
        left = y * y
        right = (x * x * x) + (self.a * x) + self.b
        return (left - right) % self.p == 0

    def compute_y(self, x) -> int | None:
        right = (x * x * x + self.a * x + self.b) % self.p
        y = modsqrt(right, self.p)
        return y

    def _add_affine_point(self, P: AffinePoint, Q: AffinePoint) -> AffinePoint:
        # s = (yP - yQ) / (xP - xQ)
        # xR = s^2 - xP - xQ
        # yR = yP + s * (xR - xP)
        delta_x = P.x - Q.x
        delta_y = P.y - Q.y
        s = delta_y * modinv(delta_x, self.p)
        res_x = (s * s - P.x - Q.x) % self.p
        res_y = (P.y + s * (res_x - P.x)) % self.p
        return -AffinePoint(self, res_x, res_y)

    def _double_affine_point(self, P: AffinePoint) -> AffinePoint:
        # s = (3 * xP^2 + a) / (2 * yP)
        # xR = s^2 - 2 * xP
        # yR = yP + s * (xR - xP)
        s = (3 * P.x * P.x + self.a) * modinv(2 * P.y, self.p)
        res_x = (s * s - 2 * P.x) % self.p
        res_y = (P.y + s * (res_x - P.x)) % self.p
        return -AffinePoint(self, res_x, res_y)

    def _neg_affine_point(self, P: AffinePoint) -> AffinePoint:
        return AffinePoint(self, P.x, -P.y % self.p)

P256 = ShortWeierstrassCurve(
    name="P256",
    a=-3,
    b=41058363725152142129326129780047268409114441015993725554835256314039467401291,
    p=0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
    n=0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551,
    G_x=0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
    # G_y=0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
    G_y=0x4fe342e2fe1a7f9baa3bc04c8a5fb42c7d1bd998f54449579b446817afbd17273
)

"""
KEYS
"""

def gen_key_pair(curve_: Curve) -> tuple[int, Point]:
    private_key = gen_private_key(curve_)
    public_key = get_public_key(private_key, curve_)
    return private_key, public_key

def gen_private_key(curve_: Curve,) -> int:
    order = curve_.n
    return random_int_exclusive(order)

def get_public_key(d: int, curve_: Curve) -> Point:
    assert 1 <= d < curve_.n
    return d * curve_.G

"""
CIPHER
"""

def ecdh_shared(self_private_key: int, other_public_key: Point) -> AffinePoint:
    return self_private_key * other_public_key
