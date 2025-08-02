import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    })
  ],
  callbacks: {
    async jwt({ token, account, profile }) {
      // Persist the Google ID token for backend verification
      if (account) {
        token.idToken = account.id_token  // This is what the backend needs
        token.accessToken = account.access_token
        token.googleId = profile?.sub
      }
      return token
    },
    async session({ session, token }) {
      // Send the ID token to the client for backend requests
      session.accessToken = token.idToken as string  // Use ID token instead
      session.user.googleId = token.googleId as string
      return session
    },
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  }
})

export { handler as GET, handler as POST }