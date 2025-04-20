import React from 'react';
import './App.css';
import SequenceInput from './components/SequenceInput';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Primer Express Replica</h1>
        <p>A tool for DNA sequence analysis and primer design</p>
      </header>
      <main className="App-main">
        <SequenceInput />
      </main>
      <footer className="App-footer">
        <p>© 2023 Primer Express Replica</p>
      </footer>
    </div>
  );
}

export default App;
