#!/usr/bin/env python3
"""Canonical method naming for paper-artifact generation."""

from __future__ import annotations

CANONICAL_METHOD_ALIASES = {
    "OURS-MFAS": "OURS_MFAS",
    "OURS MFAS": "OURS_MFAS",
    "OURS_MFAS": "OURS_MFAS",
    "OURS_MFAS_INS1": "OURS_MFAS_INS1",
    "OURS_MFAS_INS2": "OURS_MFAS_INS2",
    "OURS_MFAS_INS3": "OURS_MFAS_INS3",
    "BTL": "btl",
    "btl": "btl",
    "DavidScore": "davidScore",
    "davidScore": "davidScore",
    "PageRank": "PageRank",
    "SpringRank": "SpringRank",
    "syncRank": "syncRank",
    "serialRank": "serialRank",
    "rankCentrality": "rankCentrality",
    "eigenvectorCentrality": "eigenvectorCentrality",
    "SVD_RS": "SVD_RS",
    "SVD_NRS": "SVD_NRS",
    "DIGRAC": "DIGRAC",
    "DIGRACib": "DIGRACib",
    "ib": "ib",
    "mvr": "mvr",
    "btlDIGRAC": "btlDIGRAC",
}


def canonicalize_method_name(name: str) -> str:
    if name is None:
        return ""
    key = str(name).strip()
    return CANONICAL_METHOD_ALIASES.get(key, key)
