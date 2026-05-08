# Matrizes 3×3 homogêneas no plano.

from __future__ import annotations

import math


def mat_mul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    n = 3
    c = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            c[i][j] = sum(a[i][k] * b[k][j] for k in range(n))
    return c


def T(tx: float, ty: float) -> list[list[float]]:
    return [[1.0, 0.0, tx], [0.0, 1.0, ty], [0.0, 0.0, 1.0]]


def S(sx: float, sy: float) -> list[list[float]]:
    return [[sx, 0.0, 0.0], [0.0, sy, 0.0], [0.0, 0.0, 1.0]]


def R(theta_rad: float) -> list[list[float]]:
    c, s = math.cos(theta_rad), math.sin(theta_rad)
    return [[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]


def transform_point(M: list[list[float]], x: float, y: float) -> tuple[float, float]:
    xh = M[0][0] * x + M[0][1] * y + M[0][2]
    yh = M[1][0] * x + M[1][1] * y + M[1][2]
    return (xh, yh)


def compose_TRS(tx: float, ty: float, theta: float, sx: float, sy: float) -> list[list[float]]:
    # Ordem aplicada ao ponto: S, depois R, depois T  =>  M = T @ R @ S
    return mat_mul(mat_mul(T(tx, ty), R(theta)), S(sx, sy))
