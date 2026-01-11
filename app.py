"""
Main Flask Application
DataLeakageDetectionAndIntelligentDataPreprocessingSystem
"""
import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np

from app.modules.dataset_analyzer import DatasetAnalyzer
from app.modules.leakage_detection import LeakageDetector
from app.modules.preprocessing import DataPreprocessor
from app.modules.visualization import DataVisualizer

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['CLEANED_FOLDER'] = 'app/static/cleaned'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page - Upload dataset"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Read and validate CSV
            try:
                df = pd.read_csv(filepath)
                
                if df.empty:
                    flash('Uploaded file is empty', 'error')
                    os.remove(filepath)
                    return redirect(url_for('index'))
                
                # Store filename in session
                session['original_filename'] = filename
                session['original_filepath'] = filepath
                
                flash('File uploaded successfully!', 'success')
                return redirect(url_for('analyze'))
                
            except Exception as e:
                flash(f'Error reading CSV file: {str(e)}', 'error')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(url_for('index'))
        else:
            flash('Invalid file type. Please upload a CSV file.', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'Error during upload: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/analyze')
def analyze():
    """Analyze dataset and display profiling"""
    if 'original_filepath' not in session:
        flash('Please upload a dataset first', 'error')
        return redirect(url_for('index'))
    
    try:
        df = pd.read_csv(session['original_filepath'])
        
        # Analyze dataset
        analyzer = DatasetAnalyzer(df)
        analysis = analyzer.analyze()
        
        # Store analysis in session
        session['analysis'] = analysis
        
        return render_template('analyze.html', 
                             analysis=analysis,
                             filename=session['original_filename'],
                             df_head=df.head(10).to_html(classes='table table-striped', index=False))
        
    except Exception as e:
        flash(f'Error analyzing dataset: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/select_target', methods=['POST'])
def select_target():
    """Select target column for leakage detection"""
    target_column = request.form.get('target_column')
    
    if target_column:
        session['target_column'] = target_column
    
    return redirect(url_for('detect_leakage'))


@app.route('/detect_leakage')
def detect_leakage():
    """Detect data leakage"""
    if 'original_filepath' not in session:
        flash('Please upload a dataset first', 'error')
        return redirect(url_for('index'))
    
    try:
        df = pd.read_csv(session['original_filepath'])
        target_column = session.get('target_column')
        
        # Detect leakage
        detector = LeakageDetector(df, target_column)
        leakage_report = detector.detect_all_leakage()
        leakage_summary = detector.get_leakage_summary()
        
        # Store in session
        session['leakage_report'] = leakage_report
        session['leakage_summary'] = leakage_summary
        
        return render_template('leakage_report.html',
                             leakage_report=leakage_report,
                             leakage_summary=leakage_summary,
                             target_column=target_column)
        
    except Exception as e:
        flash(f'Error detecting leakage: {str(e)}', 'error')
        return redirect(url_for('analyze'))


@app.route('/preprocess')
def preprocess():
    """Show preprocessing options"""
    if 'original_filepath' not in session:
        flash('Please upload a dataset first', 'error')
        return redirect(url_for('index'))
    
    try:
        df = pd.read_csv(session['original_filepath'])
        
        # Get column information
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Get leakage-affected columns for removal recommendation
        leakage_report = session.get('leakage_report', [])
        high_severity_cols = []
        for issue in leakage_report:
            if issue['severity'] == 'high' and issue['affected_columns'] != ['all']:
                high_severity_cols.extend(issue['affected_columns'])
        
        return render_template('preprocess.html',
                             numeric_cols=numeric_cols,
                             categorical_cols=categorical_cols,
                             all_cols=df.columns.tolist(),
                             high_severity_cols=list(set(high_severity_cols)))
        
    except Exception as e:
        flash(f'Error loading preprocessing page: {str(e)}', 'error')
        return redirect(url_for('detect_leakage'))


@app.route('/apply_preprocessing', methods=['POST'])
def apply_preprocessing():
    """Apply preprocessing pipeline"""
    if 'original_filepath' not in session:
        flash('Please upload a dataset first', 'error')
        return redirect(url_for('index'))
    
    try:
        df = pd.read_csv(session['original_filepath'])
        
        # Initialize preprocessor
        preprocessor = DataPreprocessor(df)
        
        # Remove high-severity leakage columns
        columns_to_remove = request.form.getlist('remove_columns')
        if columns_to_remove:
            preprocessor.remove_columns(columns_to_remove)
        
        # Remove duplicates
        if request.form.get('remove_duplicates') == 'yes':
            preprocessor.remove_duplicates()
        
        # Handle missing values
        missing_strategy = request.form.get('missing_strategy')
        if missing_strategy and missing_strategy != 'none':
            preprocessor.handle_missing_values(strategy=missing_strategy)
        
        # Correct datatypes
        if request.form.get('correct_datatypes') == 'yes':
            preprocessor.correct_datatypes()
        
        # Handle outliers
        outlier_method = request.form.get('outlier_method')
        if outlier_method and outlier_method != 'none':
            preprocessor.handle_outliers(method=outlier_method)
        
        # Encode categorical variables
        encoding_method = request.form.get('encoding_method')
        if encoding_method and encoding_method != 'none':
            preprocessor.encode_categorical(method=encoding_method)
        
        # Scale features
        scaling_method = request.form.get('scaling_method')
        if scaling_method and scaling_method != 'none':
            target_col = session.get('target_column')
            # Don't scale target column
            scale_cols = [col for col in preprocessor.df.select_dtypes(include=[np.number]).columns 
                         if col != target_col]
            if scale_cols:
                preprocessor.scale_features(method=scaling_method, columns=scale_cols)
        
        # Feature selection
        feature_selection = request.form.get('feature_selection')
        if feature_selection and feature_selection != 'none':
            preprocessor.feature_selection(method=feature_selection, 
                                          target_column=session.get('target_column'))
        
        # Get processed dataframe
        cleaned_df = preprocessor.get_processed_dataframe()
        preprocessing_log = preprocessor.get_preprocessing_log()
        
        # Save cleaned dataset
        cleaned_filename = 'cleaned_' + session['original_filename']
        cleaned_filepath = os.path.join(app.config['CLEANED_FOLDER'], cleaned_filename)
        cleaned_df.to_csv(cleaned_filepath, index=False)
        
        # Store in session
        session['cleaned_filename'] = cleaned_filename
        session['cleaned_filepath'] = cleaned_filepath
        session['preprocessing_log'] = preprocessing_log
        
        flash('Preprocessing completed successfully!', 'success')
        return redirect(url_for('final_validation'))
        
    except Exception as e:
        flash(f'Error during preprocessing: {str(e)}', 'error')
        return redirect(url_for('preprocess'))


@app.route('/final_validation')
def final_validation():
    """Rerun leakage detection on cleaned dataset"""
    if 'cleaned_filepath' not in session:
        flash('Please preprocess the dataset first', 'error')
        return redirect(url_for('preprocess'))
    
    try:
        # Read cleaned dataset
        cleaned_df = pd.read_csv(session['cleaned_filepath'])
        target_column = session.get('target_column')
        
        # Rerun leakage detection
        detector = LeakageDetector(cleaned_df, target_column)
        new_leakage_report = detector.detect_all_leakage()
        new_leakage_summary = detector.get_leakage_summary()
        
        # Get preprocessing log
        preprocessing_log = session.get('preprocessing_log', [])
        
        # Check if critical leakage is resolved
        validation_status = 'PASS' if new_leakage_summary['high_severity'] == 0 else 'WARNING'
        
        return render_template('final_report.html',
                             validation_status=validation_status,
                             new_leakage_report=new_leakage_report,
                             new_leakage_summary=new_leakage_summary,
                             preprocessing_log=preprocessing_log,
                             original_summary=session.get('leakage_summary', {}),
                             cleaned_filename=session['cleaned_filename'])
        
    except Exception as e:
        flash(f'Error during validation: {str(e)}', 'error')
        return redirect(url_for('preprocess'))


@app.route('/visualize')
def visualize():
    """Show visualization dashboard"""
    if 'original_filepath' not in session:
        flash('Please upload a dataset first', 'error')
        return redirect(url_for('index'))
    
    try:
        # Choose which dataset to visualize
        dataset_type = request.args.get('dataset', 'original')
        
        if dataset_type == 'cleaned' and 'cleaned_filepath' in session:
            df = pd.read_csv(session['cleaned_filepath'])
            filename = session['cleaned_filename']
        else:
            df = pd.read_csv(session['original_filepath'])
            filename = session['original_filename']
        
        visualizer = DataVisualizer(df)
        numeric_cols = visualizer.get_numeric_columns()
        categorical_cols = visualizer.get_categorical_columns()
        
        return render_template('visualize.html',
                             dataset_type=dataset_type,
                             filename=filename,
                             numeric_cols=numeric_cols,
                             categorical_cols=categorical_cols,
                             all_cols=df.columns.tolist(),
                             has_cleaned='cleaned_filepath' in session)
        
    except Exception as e:
        flash(f'Error loading visualization: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/generate_chart', methods=['POST'])
def generate_chart():
    """Generate chart based on user selection"""
    try:
        chart_type = request.form.get('chart_type')
        dataset_type = request.form.get('dataset_type', 'original')
        
        # Load appropriate dataset
        if dataset_type == 'cleaned' and 'cleaned_filepath' in session:
            df = pd.read_csv(session['cleaned_filepath'])
        else:
            df = pd.read_csv(session['original_filepath'])
        
        visualizer = DataVisualizer(df)
        chart_json = None
        
        if chart_type == 'bar_chart':
            column = request.form.get('column')
            chart_json = visualizer.create_bar_chart(column)
        
        elif chart_type == 'line_chart':
            x_col = request.form.get('x_column')
            y_col = request.form.get('y_column')
            chart_json = visualizer.create_line_chart(x_col, y_col)
        
        elif chart_type == 'histogram':
            column = request.form.get('column')
            chart_json = visualizer.create_histogram(column)
        
        elif chart_type == 'box_plot':
            column = request.form.get('column')
            chart_json = visualizer.create_box_plot(column)
        
        elif chart_type == 'scatter_plot':
            x_col = request.form.get('x_column')
            y_col = request.form.get('y_column')
            color_col = request.form.get('color_column')
            chart_json = visualizer.create_scatter_plot(x_col, y_col, color_col)
        
        elif chart_type == 'pie_chart':
            column = request.form.get('column')
            chart_json = visualizer.create_pie_chart(column)
        
        elif chart_type == 'correlation_heatmap':
            chart_json = visualizer.create_correlation_heatmap()
        
        if chart_json:
            return jsonify({'success': True, 'chart': chart_json})
        else:
            return jsonify({'success': False, 'error': 'Failed to generate chart'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/download_cleaned')
def download_cleaned():
    """Download cleaned dataset"""
    if 'cleaned_filepath' not in session:
        flash('No cleaned dataset available', 'error')
        return redirect(url_for('index'))
    
    try:
        return send_file(session['cleaned_filepath'], 
                        as_attachment=True,
                        download_name=session['cleaned_filename'])
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('final_validation'))


@app.route('/reset')
def reset():
    """Reset session and start over"""
    # Clean up uploaded files
    if 'original_filepath' in session:
        filepath = session['original_filepath']
        if os.path.exists(filepath):
            os.remove(filepath)
    
    if 'cleaned_filepath' in session:
        filepath = session['cleaned_filepath']
        if os.path.exists(filepath):
            os.remove(filepath)
    
    session.clear()
    flash('Session reset. You can upload a new dataset.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CLEANED_FOLDER'], exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
