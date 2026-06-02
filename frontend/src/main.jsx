import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { CartProvider } from './hooks/useCart';
import { WishlistProvider } from './hooks/useWishlist';
import { ConfigProvider, theme } from 'antd';
import ruRU from 'antd/locale/ru_RU';
import { GoogleReCaptchaProvider } from 'react-google-recaptcha-v3';
import 'antd/dist/reset.css';
import './index.css';

const RECAPTCHA_SITE_KEY = import.meta.env.VITE_RECAPTCHA_SITE_KEY || '6LeIxAcTAAAAAJcZw7R3B9v9x8X9x8X9x8X9x8X9';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ConfigProvider 
        locale={ruRU}
        theme={{
          algorithm: theme.defaultAlgorithm,
          token: {
            colorPrimary: '#1890ff',
            colorLink: '#1890ff',
            borderRadius: 8,
            fontFamily: "'Inter', sans-serif",
          },
        }}
      >
        <GoogleReCaptchaProvider 
          reCaptchaKey={RECAPTCHA_SITE_KEY}
          scriptProps={{
            async: false,
            defer: false,
            appendTo: 'head',
            nonce: undefined,
          }}
        >
          <AuthProvider>
            <CartProvider>
              <WishlistProvider>
                <App />
              </WishlistProvider>
            </CartProvider>
          </AuthProvider>
        </GoogleReCaptchaProvider>
      </ConfigProvider>
    </BrowserRouter>
  </React.StrictMode>
);