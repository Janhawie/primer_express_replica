import primer3
from Bio.SeqUtils import GC
from Bio import SeqIO
from io import StringIO
import matplotlib.pyplot as plt
import numpy as np
import requests
import os
import tempfile
from typing import List, Dict, Any

def clean_fasta_sequence(fasta_content: str) -> str:
    """Clean and validate FASTA sequence."""
    try:
        # Parse FASTA from string
        fasta_io = StringIO(fasta_content)
        records = list(SeqIO.parse(fasta_io, "fasta"))
        
        if not records:
            # Try parsing as raw sequence if FASTA parsing fails
            return fasta_content.strip().upper()
        
        # Return the sequence from the first FASTA record
        return str(records[0].seq).upper()
    except Exception:
        return ""

def calculate_gc_content(sequence: str) -> float:
    """Calculate GC content of a sequence."""
    return GC(sequence)

def is_valid_probe(sequence: str) -> bool:
    """Check if a sequence is valid as a TaqMan probe."""
    if sequence.startswith('G'):
        return False
    if 'GGGG' in sequence or 'AAAAAA' in sequence:
        return False
    return True

def submit_to_blast(sequence: str) -> str:
    """Submit a sequence to NCBI BLAST."""
    try:
        # NCBI BLAST API endpoint
        url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
        
        # Parameters for BLAST submission
        params = {
            "CMD": "Put",
            "PROGRAM": "blastn",
            "DATABASE": "nt",
            "QUERY": sequence
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return "Submitted to NCBI BLAST"
        else:
            return "BLAST submission failed"
    except Exception:
        return "BLAST submission error"

def generate_gc_plot(sequence: str) -> str:
    """Generate GC content plot and save it as PNG."""
    window_size = 20
    gc_values = []
    
    # Calculate GC content for each window
    for i in range(len(sequence) - window_size + 1):
        window = sequence[i:i + window_size]
        gc = calculate_gc_content(window)
        gc_values.append(gc)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(gc_values)
    plt.title("GC Content Distribution")
    plt.xlabel("Sequence Position")
    plt.ylabel("GC Content (%)")
    plt.grid(True)
    
    # Save plot to a temporary file
    temp_file = os.path.join(tempfile.gettempdir(), "gc_plot.png")
    plt.savefig(temp_file)
    plt.close()
    
    return temp_file

def design_probe(sequence: str, start: int, length: int) -> Dict[str, Any]:
    """Design a TaqMan probe for a given region."""
    probe_size = min(length - 10, 30)  # Probe should be shorter than amplicon
    
    # Try different positions for probe
    for i in range(start + 5, start + length - probe_size - 5):
        candidate = sequence[i:i + probe_size]
        if is_valid_probe(candidate):
            return {
                "sequence": candidate,
                "gc": calculate_gc_content(candidate),
                "tm": primer3.calc_tm(candidate)
            }
    
    return None

def process_sequence(sequence: str) -> Dict[str, Any]:
    """Process a DNA sequence and return primer pairs with analysis."""
    # Primer3 settings
    primer_args = {
        'SEQUENCE_TEMPLATE': sequence,
        'PRIMER_OPT_SIZE': 20,
        'PRIMER_PICK_INTERNAL_OLIGO': 1,
        'PRIMER_MIN_SIZE': 18,
        'PRIMER_MAX_SIZE': 22,
        'PRIMER_OPT_TM': 60.0,
        'PRIMER_MIN_TM': 57.0,
        'PRIMER_MAX_TM': 63.0,
        'PRIMER_MIN_GC': 40.0,
        'PRIMER_MAX_GC': 60.0,
        'PRIMER_NUM_RETURN': 3
    }
    
    # Design primers
    primer_results = primer3.bindings.designPrimers(primer_args)
    
    primers = []
    for i in range(primer_results['PRIMER_PAIR_NUM_RETURNED']):
        forward_seq = primer_results[f'PRIMER_LEFT_{i}_SEQUENCE']
        reverse_seq = primer_results[f'PRIMER_RIGHT_{i}_SEQUENCE']
        
        # Get amplicon region
        left_start = primer_results[f'PRIMER_LEFT_{i}'][0]
        right_start = primer_results[f'PRIMER_RIGHT_{i}'][0]
        amplicon_length = right_start - left_start + len(reverse_seq)
        
        # Design probe
        probe = design_probe(sequence, left_start, amplicon_length)
        if not probe:
            continue
        
        primer_pair = {
            "forward": forward_seq,
            "reverse": reverse_seq,
            "forward_tm": primer_results[f'PRIMER_LEFT_{i}_TM'],
            "reverse_tm": primer_results[f'PRIMER_RIGHT_{i}_TM'],
            "forward_gc": calculate_gc_content(forward_seq),
            "reverse_gc": calculate_gc_content(reverse_seq),
            "penalty": primer_results[f'PRIMER_PAIR_{i}_PENALTY'],
            "probe": probe,
            "blast_forward": submit_to_blast(forward_seq),
            "blast_reverse": submit_to_blast(reverse_seq)
        }
        primers.append(primer_pair)
    
    # Generate GC content plot
    gc_plot = generate_gc_plot(sequence)
    
    return {
        "primers": primers,
        "gc_plot": gc_plot
    } 