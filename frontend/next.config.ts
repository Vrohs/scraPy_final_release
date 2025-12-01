import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,

  // Bundle optimization - only Radix UI (lucide-react optimization causes issues)
  experimental: {
    optimizePackageImports: ['@radix-ui/react-avatar', '@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', '@radix-ui/react-label', '@radix-ui/react-scroll-area', '@radix-ui/react-select', '@radix-ui/react-slot', '@radix-ui/react-switch', '@radix-ui/react-tabs'],
  },
};

export default nextConfig;
