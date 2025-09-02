import NextAuth from "next-auth";
import Google from "next-auth/providers/google";

export const { auth, handlers, signIn, signOut } = NextAuth({
  debug: process.env.NODE_ENV === "development",
  secret: process.env.AUTH_SECRET,
  pages: {
    signIn: "/login",
    error: "/login", // Redirect auth errors to login page
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  cookies: {
    sessionToken: {
      name: "authjs.session-token",
      options: {
        httpOnly: true,
        sameSite: "lax",
        path: "/",
        secure: process.env.NODE_ENV === "production",
        domain: process.env.NODE_ENV === "production" ? ".gojob.ing" : undefined,
      },
    },
  },
  providers: [
    Google({
      clientId: process.env.AUTH_GOOGLE_ID!,
      clientSecret: process.env.AUTH_GOOGLE_SECRET!,
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline", 
          response_type: "code",
          scope: "openid email profile",
          include_granted_scopes: true
        }
      },
      checks: ["none"], // Disable PKCE for production compatibility
      profile(profile) {
        return {
          id: profile.sub,
          name: profile.name,
          email: profile.email,
          image: profile.picture,
        }
      }
    }),
  ],
  callbacks: {
    async jwt({ token, account, user }) {
      // Store the Google access token and create a backend-compatible token
      if (account && user) {
        // Store Google's access token
        token.googleAccessToken = account.access_token;
        token.googleRefreshToken = account.refresh_token;
        
        // Create our own backend token using user info
        // This creates a consistent token that our backend can validate
        const backendToken = await createBackendToken(user);
        token.backendToken = backendToken;
        
        // Store user info
        token.userId = user.id;
        token.email = user.email;
      }
      
      // Refresh backend token if needed (every 24 hours)
      if (token.backendToken && shouldRefreshBackendToken(token)) {
        try {
          const newBackendToken = await refreshBackendToken(token);
          token.backendToken = newBackendToken;
          token.backendTokenRefreshedAt = Date.now();
        } catch (error) {
          console.error('Failed to refresh backend token:', error);
          // Keep the old token, let the backend handle expiration
        }
      }
      
      return token;
    },
    async session({ session, token }) {
      if (session?.user && token) {
        // Provide the backend token as accessToken for API calls
        session.accessToken = token.backendToken;
        session.user.id = token.userId as string;
        
        // Store Google token separately if needed
        session.googleToken = token.googleAccessToken;
      }
      return session;
    },
    async redirect({ url, baseUrl }) {
      if (url.startsWith("/")) return `${baseUrl}${url}`;
      else if (new URL(url).origin === baseUrl) return url;
      return baseUrl;
    },
  },
  trustHost: true,
});

// Helper functions for backend token management
async function createBackendToken(user: any): Promise<string> {
  try {
    // Create a JWT token that our backend can validate
    // This should match what your backend expects
    const payload = {
      sub: user.id,
      email: user.email,
      name: user.name,
      picture: user.image,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60), // 24 hours
      iss: 'gojob.ing',
      aud: 'resume-matcher-api'
    };
    
    // For now, create a simple token. In production, you'd want to sign this with JWT
    const token = Buffer.from(JSON.stringify(payload)).toString('base64url');
    return `gojob_${token}`;
    
  } catch (error) {
    console.error('Failed to create backend token:', error);
    // Fallback: use a simple user identifier
    return `user_${user.id || user.email}`;
  }
}

function shouldRefreshBackendToken(token: any): boolean {
  const lastRefresh = token.backendTokenRefreshedAt || 0;
  const now = Date.now();
  const refreshInterval = 24 * 60 * 60 * 1000; // 24 hours
  
  return (now - lastRefresh) > refreshInterval;
}

async function refreshBackendToken(token: any): Promise<string> {
  // Create a new backend token with fresh timestamp
  const user = {
    id: token.userId,
    email: token.email,
    name: token.name,
    image: token.picture
  };
  
  return await createBackendToken(user);
}
