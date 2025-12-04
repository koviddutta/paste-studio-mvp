"""
Reporting logic for the Paste Core module.
Placeholder for future implementation of text and PDF report generation for paste formulations.
"""

from __future__ import annotations
from .domain import DesignedPaste


def generate_text_report(designed_paste: DesignedPaste) -> str:
    """
    Generates a simple text-based report of the designed paste.
    Includes composition, metrics, and validation status.
    """
    return (
        f"Report for {designed_paste.sweet_profile.sweet_name} Paste\n(Not implemented)"
    )


def generate_pdf_report(designed_paste: DesignedPaste) -> bytes:
    """
    Generates a PDF report of the designed paste.
    Returns the PDF binary data.
    """
    return b"%PDF-1.4 ... (Not implemented)"


def format_sop_text(designed_paste: DesignedPaste) -> list[str]:
    """
    Generates a list of Standard Operating Procedure (SOP) steps
    customized for the designed paste.
    """
    return ["Step 1: Prepare ingredients (Not implemented)"]