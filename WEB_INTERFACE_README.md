# SimpleSubCipher Web Interface

A modern web interface for the SimpleSubCipher cryptanalysis tool.

## Features

### 1. Encrypt/Decrypt Tab
- **Encryption**: Convert plaintext to ciphertext with custom or random keys
- **Decryption**: Decrypt ciphertext using a known key
- **Sample Text**: Load pre-defined Czech text samples
- **Key Management**: Generate random keys or use custom permutations

### 2. Cryptanalysis Tab
- **Automatic Breaking**: Uses Metropolis-Hastings algorithm
- **Real-time Progress**: Visual progress bar during analysis
- **Fitness Visualization**: Graph showing optimization progress
- **Configurable Iterations**: Adjust between speed and accuracy (1k-50k)

### 3. Bigram Analysis Tab
- **Frequency Heatmap**: Visual representation of Czech bigram frequencies
- **Top Bigrams**: List of most common character pairs
- **Corpus Statistics**: Based on 450k+ character Krakatit text

## Running the Web Interface

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python3 web_app.py
```

3. Open in browser:
```
http://localhost:5000
```

## API Endpoints

- `POST /api/encrypt` - Encrypt plaintext
- `POST /api/decrypt` - Decrypt ciphertext
- `POST /api/analyze` - Start cryptanalysis task
- `GET /api/analyze/<task_id>` - Check analysis progress
- `GET /api/bigram_matrix` - Get bigram visualization
- `GET /api/sample_text` - Get sample texts

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, jQuery
- **Visualization**: Matplotlib, Seaborn
- **Processing**: NumPy for matrix operations

## Screenshots

The interface provides:
- Clean, modern UI with tab navigation
- Real-time cryptanalysis with progress tracking
- Interactive bigram frequency visualization
- Copy-paste functionality between tabs

## Development

To run in production mode, use a WSGI server:
```bash
gunicorn -w 4 web_app:app
```