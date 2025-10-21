import { StytchProvider, IdentityProvider, useStytchSession, useStytch } from '@stytch/react';
import { StytchUIClient } from '@stytch/vanilla-js';
import { useState, useEffect } from 'react';
import './App.css';

// Initialize Stytch client
const stytch = new StytchUIClient(import.meta.env.VITE_STYTCH_PUBLIC_TOKEN);

function LoginFlow() {
  const { session } = useStytchSession();
  const stytchClient = useStytch();
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [oauthParams, setOauthParams] = useState(null);

  console.log('ENV TOKEN:', import.meta.env.VITE_STYTCH_PUBLIC_TOKEN);
  useEffect(() => {
    // On mount, check for OAuth params in URL
    const params = new URLSearchParams(window.location.search);

    // Check if this is a Stytch OAuth callback (after Twitter login)
    const stytchTokenType = params.get('stytch_token_type');
    const stytchToken = params.get('token');

    if (stytchTokenType === 'oauth' && stytchToken) {
      console.log('🔐 Detected Stytch OAuth callback, authenticating token...');

      // Authenticate the Stytch OAuth token to create a session
      stytchClient.oauth.authenticate(stytchToken, {
        session_duration_minutes: 60,
      })
      .then(async (response) => {
        console.log('✅ Stytch session created:', response);

        // Save user profile to backend database
        console.log('🔐 Calling backend to save profile...');
        try {
          const saveResponse = await fetch(`${window.location.origin}/api/save-profile`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              session_token: response.session_token
            })
          });

          const saveData = await saveResponse.json();
          if (saveData.success) {
            console.log('✅ Profile saved successfully:', saveData.profile);
          } else {
            console.error('❌ Profile save failed:', saveData.message);
          }
        } catch (error) {
          console.error('❌ Error calling save-profile endpoint:', error);
        }

        // Restore ChatGPT OAuth params from sessionStorage
        const saved = sessionStorage.getItem('chatgpt_oauth_params');
        if (saved) {
          const restored = JSON.parse(saved);
          setOauthParams(restored);
          console.log('Restored OAuth params for IdentityProvider:', restored);

          // Build URL with OAuth params for IdentityProvider to read
          const urlWithParams = new URL(window.location.origin + window.location.pathname);
          Object.entries(restored).forEach(([key, value]) => {
            if (value) {
              urlWithParams.searchParams.set(key, value);
            }
          });

          // Update URL with OAuth params so IdentityProvider can read them
          window.history.replaceState({}, '', urlWithParams.toString());
          console.log('Updated URL with OAuth params for IdentityProvider');
        }
      })
      .catch((error) => {
        console.error('❌ Stytch authentication failed:', error);
      });

      return; // Don't process other params during Stytch callback
    }

    // If we have OAuth params (from ChatGPT), save them
    if (params.get('client_id')) {
      const savedParams = {
        response_type: params.get('response_type'),
        client_id: params.get('client_id'),
        redirect_uri: params.get('redirect_uri'),
        state: params.get('state'),
        code_challenge: params.get('code_challenge'),
        code_challenge_method: params.get('code_challenge_method'),
        resource: params.get('resource'),
      };

      sessionStorage.setItem('chatgpt_oauth_params', JSON.stringify(savedParams));
      setOauthParams(savedParams);
      console.log('Saved OAuth params:', savedParams);
    } else {
      // Try to restore from sessionStorage
      const saved = sessionStorage.getItem('chatgpt_oauth_params');
      if (saved) {
        const restored = JSON.parse(saved);
        setOauthParams(restored);
        console.log('Restored OAuth params:', restored);
      }
    }
  }, [stytchClient]);

  // Handle Twitter OAuth login
  const handleTwitterLogin = async () => {
    setIsLoggingIn(true);
    try {
      // Use clean redirect URL without query params
      const loginRedirectURL = `${window.location.origin}/login`;

      await stytchClient.oauth.twitter.start({
        login_redirect_url: loginRedirectURL,
        signup_redirect_url: loginRedirectURL,
      });
    } catch (error) {
      console.error('Twitter login failed:', error);
      setIsLoggingIn(false);
    }
  };

  // If user has a session, show IdentityProvider for consent
  if (session && oauthParams) {
    console.log('Showing IdentityProvider with session and OAuth params');
    return (
      <div>
        <IdentityProvider
          config={{
            products: ['oauth'],
            oauthOptions: {
              providers: [{
                type: 'twitter',
              }],
            },
          }}
          callbacks={{
            onEvent: (data) => {
              console.log('Stytch event:', data);
            },
            onError: (error) => {
              console.error('Stytch error:', error);
            },
          }}
        />
      </div>
    );
  }

  // If no session, show login button
  return (
    <div className="login-prompt">
      <p>First, sign in with X to continue</p>
      <button
        onClick={handleTwitterLogin}
        disabled={isLoggingIn}
        className="twitter-button"
      >
        {isLoggingIn ? 'Redirecting...' : 'Sign in with X'}
      </button>
    </div>
  );
}

function App() {
  return (
    <StytchProvider stytch={stytch}>
      <div className="app-container">
        <div className="login-card">
          <h1>🌈 Gradient Tweet MCP</h1>
          <p className="subtitle">Authorize ChatGPT to create gradient tweets</p>
          <LoginFlow />
        </div>
      </div>
    </StytchProvider>
  );
}

export default App;
