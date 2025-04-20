import React, { useState } from 'react';
import './SequenceInput.css';

const SequenceInput: React.FC = () => {
    const [sequence, setSequence] = useState<string>('');
    const [displaySequence, setDisplaySequence] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

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
            // Format and display the input sequence
            const cleanedSequence = sequence.trim();
            setDisplaySequence(cleanedSequence);

            // In a future version, we could send this to the backend
            // const formData = new FormData();
            // formData.append('sequence', cleanedSequence);
            // const response = await fetch('http://localhost:8000/design', {
            //   method: 'POST',
            //   body: formData,
            // });

            // if (!response.ok) {
            //   throw new Error('Failed to process sequence');
            // }

            // const data = await response.json();
            // Process and display results here
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

            {displaySequence && (
                <div className="sequence-display">
                    <h3>Input Sequence:</h3>
                    <pre>{displaySequence}</pre>
                </div>
            )}
        </div>
    );
};

export default SequenceInput; 