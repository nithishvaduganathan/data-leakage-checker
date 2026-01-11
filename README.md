# Data Leakage Detection and Intelligent Data Preprocessing System

A comprehensive, production-ready Flask web application for detecting data leakage in datasets and providing intelligent preprocessing pipelines for machine learning projects.

## 🚀 Features

### 1. **Dataset Analysis**
- Automatic column type detection (numerical, categorical, datetime, ID columns)
- Comprehensive dataset profiling:
  - Row and column counts
  - Missing value analysis
  - Duplicate detection
  - Data type information
  - Sample values preview

### 2. **Comprehensive Data Leakage Detection**
- **Target Leakage**: Detects features highly correlated with target variable
- **Train-Test Leakage**: Identifies duplicate rows and identifier reuse
- **Temporal Leakage**: Checks for future information in datetime columns
- **Encoding Leakage**: Warns about target encoding before data split
- **Severity Scoring**: Classifies issues as low, medium, or high severity

### 3. **Intelligent Preprocessing Pipeline**
- **Missing Value Handling**: Mean, median, mode, or drop strategies
- **Duplicate Removal**: Remove exact duplicate rows
- **Datatype Correction**: Automatic type inference and conversion
- **Outlier Handling**: IQR or Z-score methods with capping
- **Feature Scaling**: StandardScaler or MinMaxScaler
- **Encoding**: Label encoding or one-hot encoding for categorical variables
- **Feature Selection**: Correlation-based or variance-based selection

### 4. **Interactive Visualizations**
Dynamic chart generation using Plotly:
- Bar charts
- Line charts
- Histograms
- Box plots
- Scatter plots
- Pie charts
- Correlation heatmaps

### 5. **ML-Ready Dataset Export**
- Download cleaned, leakage-free datasets
- Side-by-side comparison of original vs cleaned data
- Revalidation to confirm no critical leakage
- Final validation status report

## 📋 Requirements

- Python 3.8+
- Flask 3.0.0
- Pandas 2.1.4
- NumPy 1.26.2
- Scikit-learn 1.3.2
- Plotly 5.18.0

## 🛠️ Installation

### Option 1: Using pip

```bash
# Clone the repository
git clone https://github.com/nithishvaduganathan/data-leakage-checker.git
cd data-leakage-checker

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Option 2: Using conda

```bash
# Clone the repository
git clone https://github.com/nithishvaduganathan/data-leakage-checker.git
cd data-leakage-checker

# Create conda environment
conda create -n leakage-detector python=3.8
conda activate leakage-detector

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 🚀 Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Access the web interface**:
   Open your browser and navigate to `http://localhost:5000`

3. **Upload a dataset**:
   - Click "Upload" and select a CSV file (max 50MB)
   - The system will validate and analyze the dataset

4. **Review analysis**:
   - View dataset profiling and column types
   - Select target column for leakage detection

5. **Check for leakage**:
   - Review detailed leakage report
   - Note high-severity issues that need attention

6. **Apply preprocessing**:
   - Configure preprocessing options
   - Remove high-risk columns
   - Apply cleaning operations
   - Generate cleaned dataset

7. **Validate results**:
   - Review final validation report
   - Confirm no critical leakage remains
   - Download cleaned dataset

8. **Visualize data**:
   - Create interactive charts
   - Compare original vs cleaned data
   - Export visualizations

## 📁 Project Structure

```
data-leakage-checker/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # Documentation
├── .gitignore                      # Git ignore file
└── app/
    ├── modules/
    │   ├── dataset_analyzer.py     # Dataset analysis module
    │   ├── leakage_detection.py    # Leakage detection module
    │   ├── preprocessing.py        # Preprocessing module
    │   └── visualization.py        # Visualization module
    ├── templates/
    │   ├── base.html               # Base template
    │   ├── index.html              # Upload page
    │   ├── analyze.html            # Analysis page
    │   ├── leakage_report.html     # Leakage report page
    │   ├── preprocess.html         # Preprocessing page
    │   ├── visualize.html          # Visualization page
    │   └── final_report.html       # Final validation page
    └── static/
        ├── uploads/                # Uploaded files
        └── cleaned/                # Cleaned datasets
```

## 🔒 Security Features

- Secure file upload with extension validation
- File size limits (50MB max)
- Secure filename handling using werkzeug
- Session-based data isolation
- Automatic cleanup of uploaded files on reset

## 🎨 UI Features

- Modern, responsive Bootstrap 5 design
- Gradient color schemes
- Interactive navigation
- Progress indicators
- Flash messages for user feedback
- Collapsible sections for detailed reports
- Dynamic form controls

## 🧪 Testing

To test the application with sample data:

1. Prepare a CSV file with various data types
2. Upload through the web interface
3. Follow the workflow:
   - Upload → Analysis → Leakage Detection → Preprocessing → Validation

## 📊 Leakage Types Detected

### Target Leakage
- Features with correlation > 0.95 with target
- Features with names derived from target

### Train-Test Leakage
- Duplicate rows
- High-uniqueness ID columns
- Identifier reuse issues

### Temporal Leakage
- Future information in datetime columns
- Time-series ordering warnings

### Statistical Leakage
- Low-variance features
- Highly correlated feature pairs

## 🎯 Best Practices

1. **Always remove high-severity leakage columns** before training
2. **Split data before scaling/encoding** to prevent leakage
3. **Respect temporal ordering** in time-series data
4. **Review warnings** even if no critical leakage found
5. **Validate cleaned dataset** before using in production

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📄 License

This project is open source and available under the MIT License.

## 👥 Authors

- Nithish Vaduganathan

## 🙏 Acknowledgments

- Built with Flask, Pandas, NumPy, Scikit-learn, and Plotly
- Bootstrap 5 for responsive UI
- Plotly for interactive visualizations

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Note**: This application is designed for educational and research purposes. Always validate results and use domain knowledge when making decisions about data preprocessing.
