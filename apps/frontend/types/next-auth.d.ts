import { DefaultSession, DefaultUser } from "next-auth"
import { DefaultJWT } from "next-auth/jwt"

declare module "next-auth" {
  interface Session {
    user: {
      id: string
    } & DefaultSession["user"]
    accessToken?: unknown
    googleToken?: unknown
  }

  interface User extends DefaultUser {
    id: string
  }
}

declare module "next-auth/jwt" {
  interface JWT extends DefaultJWT {
    userId?: string
    accessToken?: unknown
    refreshToken?: unknown
    googleAccessToken?: unknown
    googleRefreshToken?: unknown
    backendToken?: string
    backendTokenRefreshedAt?: number
  }
}
