import React, { useState } from 'react';
import './SequenceInput.css';

interface PrimerPair {
    forward: string;
    reverse: string;
    forward_tm: number;
    reverse_tm: number;
    forward_gc: number;
    reverse_gc: number;
    penalty: number;
    probe: {
        sequence: string;
        gc: number;
        tm: number;
    };
    blast_forward: string;
    blast_reverse: string;
}

interface PrimerResponse {
    primers: PrimerPair[];
    gc_plot: string;
}

const SequenceInput: React.FC = () => {
    const [sequence, setSequence] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [results, setResults] = useState<PrimerResponse | null>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setSequence(e.target.value);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!sequence.trim()) {
            setError('Please enter a DNA sequence in FASTA format');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('sequence', sequence.trim());
            
            const response = await fetch('http://localhost:8000/design', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Failed to process sequence');
            }

            const data = await response.json();
            setResults(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="sequence-input-container">
            <h2>DNA Sequence Input</h2>
            <p className="instruction">Enter your DNA sequence in FASTA format</p>

            <form onSubmit={handleSubmit}>
                <textarea
                    value={sequence}
                    onChange={handleInputChange}
                    placeholder=">Sequence_Name
ATGCTAGCTAGCTAGCTGACTAGCTAGCTAG..."
                    rows={10}
                    className="sequence-textarea"
                />

                <button
                    type="submit"
                    className="submit-button"
                    disabled={isLoading}
                >
                    {isLoading ? 'Processing...' : 'Submit Sequence'}
                </button>
            </form>

            {error && <div className="error-message">{error}</div>}

            {results && (
                <div className="results-container">
                    <h3>Results:</h3>
                    {results.primers.map((primer, index) => (
                        <div key={index} className="primer-pair">
                            <h4>Primer Pair {index + 1}</h4>
                            <div className="primer-details">
                                <div>
                                    <h5>Forward Primer</h5>
                                    <p>Sequence: {primer.forward}</p>
                                    <p>Tm: {primer.forward_tm}°C</p>
                                    <p>GC Content: {primer.forward_gc}%</p>
                                    <p>BLAST Status: {primer.blast_forward}</p>
                                </div>
                                <div>
                                    <h5>Reverse Primer</h5>
                                    <p>Sequence: {primer.reverse}</p>
                                    <p>Tm: {primer.reverse_tm}°C</p>
                                    <p>GC Content: {primer.reverse_gc}%</p>
                                    <p>BLAST Status: {primer.blast_reverse}</p>
                                </div>
                                <div>
                                    <h5>Probe</h5>
                                    <p>Sequence: {primer.probe.sequence}</p>
                                    <p>Tm: {primer.probe.tm}°C</p>
                                    <p>GC Content: {primer.probe.gc}%</p>
                                </div>
                                <p>Penalty Score: {primer.penalty}</p>
                            </div>
                        </div>
                    ))}
                    <div className="gc-plot">
                        <h4>GC Content Plot</h4>
                        <img src={`data:image/png;base64,${results.gc_plot}`} alt="GC Content Plot" />
                    </div>
                </div>
            )}
        </div>
    );
};

export default SequenceInput; 