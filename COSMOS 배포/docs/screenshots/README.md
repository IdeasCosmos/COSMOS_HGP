# COSMOS Screenshots

This directory contains screenshots and visual documentation for the COSMOS Visualization System.

## 📸 Screenshot Gallery

### Dashboard Overview
- **File**: `dashboard-overview.png`
- **Description**: Main dashboard showing real-time metrics and visualizations
- **Features**: Korean/English language toggle, real-time metrics, visualization cards

### Heatmap Visualization
- **File**: `heatmap.png`
- **Description**: Layer×Time heatmap with impact intensity visualization
- **Features**: 7-layer system, color-coded impact values, time-based analysis

### Event Timeline
- **File**: `timeline.png`
- **Description**: Event timeline showing distribution across layers
- **Features**: Scatter plot visualization, layer-based organization, impact intensity

### Codon Analysis
- **File**: `codon-analysis.png`
- **Description**: Codon pattern frequency analysis
- **Features**: Bar chart visualization, top codon patterns, frequency analysis

### API Documentation
- **File**: `api-docs.png`
- **Description**: Interactive API documentation (Swagger UI)
- **Features**: Endpoint documentation, interactive testing, schema definitions

### Performance Metrics
- **File**: `performance-metrics.png`
- **Description**: System performance and benchmark results
- **Features**: Response times, memory usage, processing speeds

## 🎯 How to Generate Screenshots

### 1. Start the System
```bash
# Start FastAPI server
python main_viz.py

# Or start Flask server
python simple_server.py
```

### 2. Generate Test Data
```bash
# Generate test data
python generate_test_data.py

# Generate visualizations
python -m viz.log_to_map
```

### 3. Access Dashboards
- **Korean Dashboard**: http://localhost:8000
- **English Dashboard**: http://localhost:8000/en
- **API Documentation**: http://localhost:8000/docs

### 4. Take Screenshots
1. Open the dashboard in your browser
2. Take full-page screenshots
3. Save with descriptive filenames
4. Update this README with new screenshots

## 📋 Screenshot Checklist

- [ ] Dashboard overview (Korean)
- [ ] Dashboard overview (English)
- [ ] Heatmap visualization
- [ ] Event timeline
- [ ] Codon analysis
- [ ] API documentation
- [ ] Performance metrics
- [ ] Mobile responsive view
- [ ] Error states
- [ ] Loading states

## 🎨 Screenshot Guidelines

### Resolution
- **Desktop**: 1920x1080 or higher
- **Mobile**: 375x667 (iPhone SE) or 414x896 (iPhone 11)

### Format
- **Format**: PNG (preferred) or JPG
- **Quality**: High resolution for documentation
- **Compression**: Optimize for web use

### Content
- **Clean UI**: Remove personal data, use test data
- **Consistent styling**: Use default themes
- **Clear labels**: Ensure text is readable
- **Full context**: Show complete interface elements

## 📝 Adding New Screenshots

1. Take the screenshot
2. Save with descriptive filename
3. Add entry to this README
4. Update main README.md if needed
5. Commit to version control

## 🔧 Tools for Screenshots

### Browser Extensions
- **Full Page Screen Capture** (Chrome)
- **FireShot** (Firefox)
- **Awesome Screenshot** (Cross-browser)

### Desktop Tools
- **Snipping Tool** (Windows)
- **Screenshot** (macOS)
- **Shutter** (Linux)

### Online Tools
- **Screenshot.guru**
- **Screenshot.rocks**
- **Placeit.net**

---

**Note**: Keep screenshots up-to-date with the latest UI changes and ensure they represent the current system accurately.
