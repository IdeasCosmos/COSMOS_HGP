import React from 'react';

export default function SimpleTest() {
  return (
    <div style={{
      padding: '50px',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f0f0f0',
      minHeight: '100vh'
    }}>
      <h1 style={{color: '#333'}}>🌌 COSMOS 테스트 페이지</h1>
      <div style={{
        background: 'white',
        padding: '20px',
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <h2>✅ React가 정상적으로 작동합니다!</h2>
        <p>현재 시간: {new Date().toLocaleString()}</p>
        <p>이 메시지가 보이면 React 컴포넌트가 정상적으로 렌더링되고 있습니다.</p>
      </div>
    </div>
  );
}
