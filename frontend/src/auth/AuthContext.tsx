import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { login as apiLogin, fetchMe, type User } from "../api/client";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("ara_token");
    if (!token) {
      setLoading(false);
      return;
    }
    fetchMe()
      .then(setUser)
      .catch(() => localStorage.removeItem("ara_token"))
      .finally(() => setLoading(false));
  }, []);

  async function signIn(email: string, password: string) {
    const { access_token, user: loggedInUser } = await apiLogin(email, password);
    localStorage.setItem("ara_token", access_token);
    setUser(loggedInUser);
  }

  function signOut() {
    localStorage.removeItem("ara_token");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
