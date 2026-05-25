import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { CartProvider } from './hooks/useCart';
import { ConfigProvider, theme } from 'antd';
import 'antd/dist/reset.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ConfigProvider theme={{ algorithm: theme.defaultAlgorithm }}>
        <AuthProvider>
          <CartProvider>
            <App />
          </CartProvider>
        </AuthProvider>
      </ConfigProvider>
    </BrowserRouter>
  </React.StrictMode>
);