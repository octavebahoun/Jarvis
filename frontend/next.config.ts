import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // La démo a vécu quelques minutes sur /demo : ce lien mène désormais à l'accueil.
  async redirects() {
    return [{ source: "/demo", destination: "/", permanent: true }];
  },
};

export default nextConfig;
