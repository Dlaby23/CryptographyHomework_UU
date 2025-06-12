"""
Web interface for SimpleSubCipher cryptanalysis tool.
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import numpy as np
from substitution_cipher import SubstitutionCipher, BigramAnalysis
from cryptanalysis import MetropolisHastingsCryptanalysis, load_reference_matrix
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime
import threading
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Global storage for analysis tasks
analysis_tasks = {}

class AnalysisTask:
    def __init__(self, task_id):
        self.task_id = task_id
        self.status = 'pending'
        self.progress = 0
        self.result = None
        self.error = None
        self.start_time = datetime.now()
        
def create_bigram_heatmap(matrix, alphabet):
    """Create a base64 encoded heatmap of the bigram matrix."""
    plt.figure(figsize=(10, 8))
    
    # Use log scale for better visualization
    log_matrix = np.log10(matrix + 1e-10)
    
    sns.heatmap(log_matrix, 
                xticklabels=list(alphabet),
                yticklabels=list(alphabet),
                cmap='viridis',
                cbar_kws={'label': 'log10(probability)'})
    
    plt.title('Czech Bigram Frequency Matrix', fontsize=14)
    plt.xlabel('Second Character')
    plt.ylabel('First Character')
    plt.tight_layout()
    
    # Convert to base64
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

def run_cryptanalysis(task_id, ciphertext, iterations):
    """Run cryptanalysis in background thread."""
    task = analysis_tasks[task_id]
    
    try:
        # Load reference matrix
        ref_matrix = load_reference_matrix()
        cipher = SubstitutionCipher()
        
        # Initialize cryptanalysis
        cryptanalysis = MetropolisHastingsCryptanalysis(ref_matrix, temperature=2.0)
        
        # Custom metropolis hastings with progress tracking
        current_key = cipher.generate_random_key()
        current_text = cipher.decrypt(ciphertext, current_key)
        current_fitness = cryptanalysis._calculate_fitness(current_text)
        
        best_key = current_key.copy()
        best_text = current_text
        best_fitness = current_fitness
        
        fitness_history = []
        
        for i in range(iterations):
            # Update progress
            task.progress = int((i / iterations) * 100)
            
            # M-H step
            candidate_key = cryptanalysis._swap_two_chars(current_key)
            candidate_text = cipher.decrypt(ciphertext, candidate_key)
            candidate_fitness = cryptanalysis._calculate_fitness(candidate_text)
            
            delta = candidate_fitness - current_fitness
            
            if delta > 0 or np.random.random() < np.exp(delta / cryptanalysis.temperature):
                current_key = candidate_key
                current_text = candidate_text
                current_fitness = candidate_fitness
                
                if current_fitness > best_fitness:
                    best_key = current_key.copy()
                    best_text = current_text
                    best_fitness = current_fitness
            
            fitness_history.append(best_fitness)
            
            # Adaptive temperature
            if i % 1000 == 0:
                cryptanalysis.temperature = 2.0 * (1 - i / iterations)
        
        # Create fitness plot
        plt.figure(figsize=(10, 6))
        plt.plot(fitness_history)
        plt.title('Fitness Evolution During Cryptanalysis')
        plt.xlabel('Iteration')
        plt.ylabel('Fitness Score')
        plt.grid(True, alpha=0.3)
        
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100)
        img.seek(0)
        fitness_plot = base64.b64encode(img.getvalue()).decode()
        plt.close()
        
        task.result = {
            'plaintext': best_text,
            'key': cipher.key_to_string(best_key),
            'fitness': best_fitness,
            'fitness_plot': fitness_plot,
            'iterations': iterations
        }
        task.status = 'completed'
        
    except Exception as e:
        task.error = str(e)
        task.status = 'failed'

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/encrypt', methods=['POST'])
def encrypt():
    """Encrypt text endpoint."""
    data = request.json
    plaintext = data.get('plaintext', '').upper()
    key_string = data.get('key', '')
    
    cipher = SubstitutionCipher()
    
    # Preprocess text
    plaintext = cipher.preprocess_text(plaintext)
    
    # Generate or use provided key
    if key_string:
        try:
            key = cipher.string_to_key(key_string)
        except:
            return jsonify({'error': 'Invalid key format'}), 400
    else:
        key = cipher.generate_random_key()
        key_string = cipher.key_to_string(key)
    
    ciphertext = cipher.encrypt(plaintext, key)
    
    return jsonify({
        'plaintext': plaintext,
        'ciphertext': ciphertext,
        'key': key_string
    })

@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    """Decrypt text endpoint."""
    data = request.json
    ciphertext = data.get('ciphertext', '').upper()
    key_string = data.get('key', '')
    
    if not key_string:
        return jsonify({'error': 'Key is required for decryption'}), 400
    
    cipher = SubstitutionCipher()
    
    try:
        key = cipher.string_to_key(key_string)
        plaintext = cipher.decrypt(ciphertext, key)
        
        return jsonify({
            'ciphertext': ciphertext,
            'plaintext': plaintext,
            'key': key_string
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Start cryptanalysis task."""
    data = request.json
    ciphertext = data.get('ciphertext', '').upper()
    iterations = data.get('iterations', 10000)
    
    if not ciphertext:
        return jsonify({'error': 'Ciphertext is required'}), 400
    
    # Create new task
    task_id = str(uuid.uuid4())
    task = AnalysisTask(task_id)
    analysis_tasks[task_id] = task
    
    # Start analysis in background
    thread = threading.Thread(
        target=run_cryptanalysis, 
        args=(task_id, ciphertext, iterations)
    )
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/api/analyze/<task_id>')
def get_analysis_status(task_id):
    """Get analysis task status."""
    task = analysis_tasks.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    response = {
        'task_id': task_id,
        'status': task.status,
        'progress': task.progress
    }
    
    if task.status == 'completed':
        response.update(task.result)
    elif task.status == 'failed':
        response['error'] = task.error
    
    return jsonify(response)

@app.route('/api/bigram_matrix')
def get_bigram_matrix():
    """Get bigram matrix visualization."""
    try:
        ref_matrix = load_reference_matrix()
        analyzer = BigramAnalysis()
        
        plot_url = create_bigram_heatmap(ref_matrix, analyzer.alphabet)
        
        # Get top bigrams
        flat_indices = np.argsort(ref_matrix.ravel())[-20:][::-1]
        indices = np.unravel_index(flat_indices, ref_matrix.shape)
        
        top_bigrams = []
        for i in range(20):
            row, col = indices[0][i], indices[1][i]
            bigram = analyzer.alphabet[row] + analyzer.alphabet[col]
            prob = ref_matrix[row, col]
            top_bigrams.append({
                'bigram': bigram,
                'probability': float(prob),
                'percentage': float(prob * 100)
            })
        
        return jsonify({
            'plot': plot_url,
            'top_bigrams': top_bigrams
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sample_text')
def get_sample_text():
    """Get sample Czech text."""
    samples = [
        "TENTO_TEXT_JE_UKAZKOVY_PRIKLAD_PRO_DEMONSTRACI_SIFROVANI",
        "AHOJ_JAK_SE_MAS_DNES_JE_KRASNY_DEN_A_JA_JSEM_STASTNY",
        "KRYPTOGRAFIE_JE_VELMI_ZAJIMAVA_OBLAST_INFORMATIKY",
        "METROPOLIS_HASTINGS_ALGORITMUS_JE_MOCNY_NASTROJ_PRO_OPTIMALIZACI"
    ]
    
    return jsonify({'samples': samples})

if __name__ == '__main__':
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    # Create HTML template
    with open('templates/index.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SimpleSubCipher - Web Interface</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .container {
            max-width: 1200px;
        }
        .card {
            box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
            margin-bottom: 1.5rem;
        }
        .monospace {
            font-family: 'Courier New', monospace;
            background-color: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
        }
        .progress {
            height: 25px;
        }
        .bigram-plot {
            max-width: 100%;
            height: auto;
        }
        #fitness-plot {
            max-width: 100%;
            height: auto;
        }
        .alphabet-display {
            letter-spacing: 0.5rem;
            font-size: 1.2rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-lock"></i> SimpleSubCipher
            </span>
            <span class="navbar-text">
                Monoalphabetic Substitution Cipher Cryptanalysis
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Alphabet Display -->
        <div class="card">
            <div class="card-body text-center">
                <h6 class="card-subtitle mb-2 text-muted">Supported Alphabet</h6>
                <div class="monospace alphabet-display">ABCDEFGHIJKLMNOPQRSTUVWXYZ_</div>
            </div>
        </div>

        <!-- Tab Navigation -->
        <ul class="nav nav-tabs" id="myTab" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="encrypt-tab" data-bs-toggle="tab" data-bs-target="#encrypt" type="button">
                    <i class="fas fa-lock"></i> Encrypt/Decrypt
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="analyze-tab" data-bs-toggle="tab" data-bs-target="#analyze" type="button">
                    <i class="fas fa-chart-line"></i> Cryptanalysis
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="bigram-tab" data-bs-toggle="tab" data-bs-target="#bigram" type="button">
                    <i class="fas fa-table"></i> Bigram Analysis
                </button>
            </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content" id="myTabContent">
            <!-- Encrypt/Decrypt Tab -->
            <div class="tab-pane fade show active" id="encrypt" role="tabpanel">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Encrypt Text</h5>
                        <div class="mb-3">
                            <label for="plaintext" class="form-label">Plaintext</label>
                            <textarea class="form-control monospace" id="plaintext" rows="3" 
                                placeholder="Enter text to encrypt..."></textarea>
                            <button class="btn btn-sm btn-secondary mt-2" onclick="loadSampleText()">
                                Load Sample Text
                            </button>
                        </div>
                        <div class="mb-3">
                            <label for="encrypt-key" class="form-label">Key (leave empty for random)</label>
                            <input type="text" class="form-control monospace" id="encrypt-key" 
                                placeholder="e.g., QWERTYUIOPASDFGHJKLZXCVBNM_">
                        </div>
                        <button class="btn btn-primary" onclick="encryptText()">
                            <i class="fas fa-lock"></i> Encrypt
                        </button>
                        <div id="encrypt-result" class="mt-3"></div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Decrypt Text</h5>
                        <div class="mb-3">
                            <label for="ciphertext" class="form-label">Ciphertext</label>
                            <textarea class="form-control monospace" id="ciphertext" rows="3" 
                                placeholder="Enter encrypted text..."></textarea>
                        </div>
                        <div class="mb-3">
                            <label for="decrypt-key" class="form-label">Key (required)</label>
                            <input type="text" class="form-control monospace" id="decrypt-key" 
                                placeholder="e.g., QWERTYUIOPASDFGHJKLZXCVBNM_" required>
                        </div>
                        <button class="btn btn-success" onclick="decryptText()">
                            <i class="fas fa-unlock"></i> Decrypt
                        </button>
                        <div id="decrypt-result" class="mt-3"></div>
                    </div>
                </div>
            </div>

            <!-- Cryptanalysis Tab -->
            <div class="tab-pane fade" id="analyze" role="tabpanel">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Automatic Cryptanalysis</h5>
                        <p class="text-muted">Uses Metropolis-Hastings algorithm with Czech bigram frequencies</p>
                        
                        <div class="mb-3">
                            <label for="analyze-ciphertext" class="form-label">Ciphertext to Analyze</label>
                            <textarea class="form-control monospace" id="analyze-ciphertext" rows="4" 
                                placeholder="Enter encrypted text to break..."></textarea>
                        </div>
                        
                        <div class="mb-3">
                            <label for="iterations" class="form-label">Iterations</label>
                            <input type="number" class="form-control" id="iterations" 
                                value="10000" min="1000" max="50000" step="1000">
                            <small class="text-muted">More iterations = better results but slower</small>
                        </div>
                        
                        <button class="btn btn-primary" onclick="startAnalysis()">
                            <i class="fas fa-search"></i> Start Cryptanalysis
                        </button>
                        
                        <div id="analysis-progress" class="mt-3" style="display: none;">
                            <div class="progress">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                    role="progressbar" style="width: 0%">0%</div>
                            </div>
                        </div>
                        
                        <div id="analysis-result" class="mt-3"></div>
                    </div>
                </div>
            </div>

            <!-- Bigram Tab -->
            <div class="tab-pane fade" id="bigram" role="tabpanel">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Czech Bigram Frequency Analysis</h5>
                        <p class="text-muted">Based on Krakatit corpus (450k+ characters)</p>
                        
                        <button class="btn btn-primary mb-3" onclick="loadBigramMatrix()">
                            <i class="fas fa-chart-bar"></i> Load Bigram Matrix
                        </button>
                        
                        <div id="bigram-result"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        let currentTaskId = null;
        let progressInterval = null;

        function encryptText() {
            const plaintext = $('#plaintext').val();
            const key = $('#encrypt-key').val();
            
            $.ajax({
                url: '/api/encrypt',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ plaintext, key }),
                success: function(data) {
                    $('#encrypt-result').html(`
                        <div class="alert alert-success">
                            <h6>Encryption Result</h6>
                            <p><strong>Processed Text:</strong><br>
                                <span class="monospace">${data.plaintext}</span></p>
                            <p><strong>Ciphertext:</strong><br>
                                <span class="monospace">${data.ciphertext}</span></p>
                            <p><strong>Key Used:</strong><br>
                                <span class="monospace">${data.key}</span></p>
                            <button class="btn btn-sm btn-secondary" 
                                onclick="copyToDecrypt('${data.ciphertext}', '${data.key}')">
                                Copy to Decrypt Tab
                            </button>
                        </div>
                    `);
                },
                error: function(xhr) {
                    $('#encrypt-result').html(`
                        <div class="alert alert-danger">
                            Error: ${xhr.responseJSON.error}
                        </div>
                    `);
                }
            });
        }

        function decryptText() {
            const ciphertext = $('#ciphertext').val();
            const key = $('#decrypt-key').val();
            
            $.ajax({
                url: '/api/decrypt',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ ciphertext, key }),
                success: function(data) {
                    $('#decrypt-result').html(`
                        <div class="alert alert-success">
                            <h6>Decryption Result</h6>
                            <p><strong>Plaintext:</strong><br>
                                <span class="monospace">${data.plaintext}</span></p>
                        </div>
                    `);
                },
                error: function(xhr) {
                    $('#decrypt-result').html(`
                        <div class="alert alert-danger">
                            Error: ${xhr.responseJSON.error}
                        </div>
                    `);
                }
            });
        }

        function startAnalysis() {
            const ciphertext = $('#analyze-ciphertext').val();
            const iterations = $('#iterations').val();
            
            if (!ciphertext) {
                alert('Please enter ciphertext to analyze');
                return;
            }
            
            $('#analysis-progress').show();
            $('#analysis-result').empty();
            
            $.ajax({
                url: '/api/analyze',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ ciphertext, iterations: parseInt(iterations) }),
                success: function(data) {
                    currentTaskId = data.task_id;
                    checkProgress();
                }
            });
        }

        function checkProgress() {
            if (progressInterval) clearInterval(progressInterval);
            
            progressInterval = setInterval(function() {
                $.get(`/api/analyze/${currentTaskId}`, function(data) {
                    const progressBar = $('.progress-bar');
                    progressBar.css('width', data.progress + '%');
                    progressBar.text(data.progress + '%');
                    
                    if (data.status === 'completed') {
                        clearInterval(progressInterval);
                        $('#analysis-progress').hide();
                        showAnalysisResult(data);
                    } else if (data.status === 'failed') {
                        clearInterval(progressInterval);
                        $('#analysis-progress').hide();
                        $('#analysis-result').html(`
                            <div class="alert alert-danger">
                                Analysis failed: ${data.error}
                            </div>
                        `);
                    }
                });
            }, 500);
        }

        function showAnalysisResult(data) {
            $('#analysis-result').html(`
                <div class="alert alert-success">
                    <h6>Cryptanalysis Complete!</h6>
                    <p><strong>Recovered Plaintext:</strong><br>
                        <span class="monospace">${data.plaintext}</span></p>
                    <p><strong>Found Key:</strong><br>
                        <span class="monospace">${data.key}</span></p>
                    <p><strong>Final Fitness Score:</strong> ${data.fitness.toFixed(4)}</p>
                    <p><strong>Iterations:</strong> ${data.iterations}</p>
                    
                    <h6 class="mt-3">Fitness Evolution</h6>
                    <img src="data:image/png;base64,${data.fitness_plot}" 
                        class="img-fluid" id="fitness-plot">
                </div>
            `);
        }

        function loadBigramMatrix() {
            $('#bigram-result').html('<div class="text-center"><div class="spinner-border"></div></div>');
            
            $.get('/api/bigram_matrix', function(data) {
                let bigramTable = '<h6>Top 20 Bigrams</h6><table class="table table-sm"><thead><tr><th>Bigram</th><th>Probability</th></tr></thead><tbody>';
                
                data.top_bigrams.forEach(function(item) {
                    bigramTable += `<tr><td class="monospace">${item.bigram}</td><td>${item.percentage.toFixed(2)}%</td></tr>`;
                });
                
                bigramTable += '</tbody></table>';
                
                $('#bigram-result').html(`
                    <div class="row">
                        <div class="col-md-8">
                            <img src="data:image/png;base64,${data.plot}" class="bigram-plot img-fluid">
                        </div>
                        <div class="col-md-4">
                            ${bigramTable}
                        </div>
                    </div>
                `);
            });
        }

        function loadSampleText() {
            $.get('/api/sample_text', function(data) {
                const randomSample = data.samples[Math.floor(Math.random() * data.samples.length)];
                $('#plaintext').val(randomSample);
            });
        }

        function copyToDecrypt(ciphertext, key) {
            $('#ciphertext').val(ciphertext);
            $('#decrypt-key').val(key);
            $('button[data-bs-target="#encrypt"]').removeClass('active');
            $('#encrypt').removeClass('show active');
            $('button[data-bs-target="#analyze"]').addClass('active');
            $('#analyze').addClass('show active');
        }
    </script>
</body>
</html>''')
    
    print("Starting web server on http://localhost:5000")
    app.run(debug=True, port=5000)