import React from 'react'
import ReactDOM from 'react-dom/client'
import BeadFlowMessengerFull from './BeadFlowMessenger.jsx'
import './index.css'

// 에러 바운더리
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('React Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{padding: '50px', fontFamily: 'Arial'}}>
          <h1 style={{color: '#ef4444'}}>⚠️ 에러 발생</h1>
          <pre style={{background: '#fee', padding: '20px', borderRadius: '8px'}}>
            {this.state.error?.toString()}
          </pre>
          <button onClick={() => window.location.reload()}>새로고침</button>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BeadFlowMessengerFull />
    </ErrorBoundary>
  </React.StrictMode>,
)

